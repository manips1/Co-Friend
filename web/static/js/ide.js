var defaultUrl = localStorageGetItem("api-url") || "https://ce.judge0.com";
var apiUrl = defaultUrl;
var wait = localStorageGetItem("wait") || true;
var check_timeout = 300;

var blinkStatusLine = ((localStorageGetItem("blink") || "true") === "true");
var editorMode = localStorageGetItem("editorMode") || "normal";
var editorModeObject = null;

var fontSize = 14;

var MonacoVim;
var MonacoEmacs;

var layout;

var sourceEditor;
var stdinEditor;
var stdoutEditor;

var isEditorDirty = false;
var currentLanguageId;

var $selectLanguage;
var $compilerOptions;
var $commandLineArguments;
var $insertTemplateBtn;
var $runBtn;
var $navigationMessage;
var $updates;
var $statusLine;

var timeStart;
var timeEnd;

var messagesData;

var layoutConfig = {
    settings: {
        showPopoutIcon: false,
        reorderEnabled: true
    },
    dimensions: {
        borderWidth: 3,
        headerHeight: 22
    },
    content: [{
        type: "column",
        content: [{
            type: "component",
            height: 70,
            componentName: "source",
            id: "source",
            title: "SOURCE",
            isClosable: false,
            componentState: {
                readOnly: false
            }
        }, {
            type: "stack",
            content: [{
                type: "component",
                componentName: "stdin",
                id: "stdin",
                title: "Input",
                isClosable: false,
                componentState: {
                    readOnly: false
                }
            }, {
                type: "component",
                componentName: "stdout",
                id: "stdout",
                title: "Output",
                isClosable: false,
                componentState: {
                    readOnly: true
                }
            }]
        }]
    }]
};

function encode(str) {
    return btoa(unescape(encodeURIComponent(str || "")));
}

function decode(bytes) {
    var escaped = escape(atob(bytes || ""));
    try {
        return decodeURIComponent(escaped);
    } catch {
        return unescape(escaped);
    }
}

function localStorageSetItem(key, value) {
  try {
    localStorage.setItem(key, value);
  } catch (ignorable) {
  }
}

function localStorageGetItem(key) {
  try {
    return localStorage.getItem(key);
  } catch (ignorable) {
    return null;
  }
}

function showMessages() {
    var width = $updates.offset().left - parseFloat($updates.css("padding-left")) -
                $navigationMessage.parent().offset().left - parseFloat($navigationMessage.parent().css("padding-left")) - 5;

    if (width < 200 || messagesData === undefined) {
        return;
    }

    var messages = messagesData["messages"];

    $navigationMessage.css("animation-duration", messagesData["duration"]);
    $navigationMessage.parent().width(width - 5);

    var combinedMessage = "";
    for (var i = 0; i < messages.length; ++i) {
        combinedMessage += `${messages[i]}`;
        if (i != messages.length - 1) {
            combinedMessage += "&nbsp".repeat(Math.min(200, messages[i].length));
        }
    }

    $navigationMessage.html(combinedMessage);
}

function loadMessages() {
    $.ajax({
        url: `https://minio.judge0.com/public/ide/messages.json?${Date.now()}`,
        type: "GET",
        headers: {
            "Accept": "application/json"
        },
        success: function (data, textStatus, jqXHR) {
            messagesData = data;
            showMessages();
        }
    });
}

function showError(title, content) {
    $("#site-modal #title").html(title);
    $("#site-modal .content").html(content);
    $("#site-modal").modal("show");
}

function handleError(jqXHR, textStatus, errorThrown) {
    showError(`${jqXHR.statusText} (${jqXHR.status})`, `<pre>${JSON.stringify(jqXHR, null, 4)}</pre>`);
}

function handleRunError(jqXHR, textStatus, errorThrown) {
    handleError(jqXHR, textStatus, errorThrown);
    $runBtn.removeClass("loading");
}

function handleResult(data) {
    timeEnd = performance.now();
    console.log("It took " + (timeEnd - timeStart) + " ms to get submission result.");

    var status = data.status;
    var stdout = data.stdout;
    var compile_output = data.compile_output;
    var time = (data.time === null ? "-" : data.time + "s");
    var memory = (data.memory === null ? "-" : data.memory + "KB");

    $statusLine.html(`${status.description}, ${time}, ${memory}`);

    if (blinkStatusLine) {
        $statusLine.addClass("blink");
        setTimeout(function() {
            blinkStatusLine = false;
            localStorageSetItem("blink", "false");
            $statusLine.removeClass("blink");
        }, 3000);
    }

    var output = [compile_output, stdout].join("\n").trim();

    stdoutEditor.setValue(output);

    if (output !== "") {
        var dot = document.getElementById("stdout-dot");
        if (!dot.parentElement.classList.contains("lm_active")) {
            dot.hidden = false;
        }
    }

    $runBtn.removeClass("loading");
}

function getIdFromURI() {
  var uri = location.search.substr(1).trim();
  return uri.split("&")[0];
}

function downloadSource() {
    var value = parseInt($selectLanguage.val());
    download(sourceEditor.getValue(), fileNames[value], "text/plain");
}

function loadSavedSource() {
    snippet_id = getIdFromURI();

    if (snippet_id.length == 36) {
        $.ajax({
            url: apiUrl + "/submissions/" + snippet_id + "?fields=source_code,language_id,stdin,stdout,stderr,compile_output,message,time,memory,status,compiler_options,command_line_arguments&base64_encoded=true",
            type: "GET",
            success: function(data, textStatus, jqXHR) {
                sourceEditor.setValue(decode(data["source_code"]));
                $selectLanguage.dropdown("set selected", data["language_id"]);
                $compilerOptions.val(data["compiler_options"]);
                $commandLineArguments.val(data["command_line_arguments"]);
                stdinEditor.setValue(decode(data["stdin"]));
                stdoutEditor.setValue(decode(data["stdout"]));
                var time = (data.time === null ? "-" : data.time + "s");
                var memory = (data.memory === null ? "-" : data.memory + "KB");
                $statusLine.html(`${data.status.description}, ${time}, ${memory}`);
                changeEditorLanguage();
            },
            error: handleRunError
        });
    } else {
        loadRandomLanguage();
    }
}

function run() {
    if (sourceEditor.getValue().trim() === "") {
        showError("Error", "Source code can't be empty!");
        return;
    } else {
        $runBtn.addClass("loading");
    }

    document.getElementById("stdout-dot").hidden = true;

    stdoutEditor.setValue("");

    var x = layout.root.getItemsById("stdout")[0];
    x.parent.header.parent.setActiveContentItem(x);

    var sourceValue = sourceEditor.getValue();
    var stdinValue = stdinEditor.getValue();
    var languageId = resolveLanguageId($selectLanguage.val());
    var compilerOptions = $compilerOptions.val();
    var commandLineArguments = $commandLineArguments.val();

    if (parseInt(languageId) === 44) {
        sourceValue = sourceEditor.getValue();
    }

    //csrf token
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = cookies[i].trim();
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    var csrftoken = getCookie('csrftoken');

    var data = {
        type: 'run',
        source_code: sourceValue,
        language_id: languageId,
        stdin: stdinValue,
        compiler_options: compilerOptions,
        command_line_arguments: commandLineArguments,
        redirect_stderr_to_stdout: true,
        csrfmiddlewaretoken: csrftoken
    };

    var sendRequest = function(data) {
        $.ajaxSetup({
            headers: { "X-CSRFToken": csrftoken }
          });
        timeStart = performance.now();
        $.ajax({
            url: "",
            type: "POST",
            async: true,
            contentType: "application/json",
            data: JSON.stringify(data),
            xhrFields: {
                withCredentials: apiUrl.indexOf("/secure") != -1 ? true : false
            },

            success: function (data, textStatus, jqXHR) {
                console.log(`Your submission token is: ${data.token}`);
                
                if (wait == true) {
                    handleResult(data);
                } else {
                    setTimeout(fetchSubmission.bind(null, data.token), check_timeout);
                }
                
            },
            error: handleRunError

        });
    }
    // 임시
    //$runBtn.removeClass("loading");
   
    sendRequest(data);
}

function fetchSubmission(submission_token) {
    $.ajax({
        url: apiUrl + "/submissions/" + submission_token + "?base64_encoded=true",
        type: "GET",
        async: true,
        success: function (data, textStatus, jqXHR) {
            if (data.status.id <= 2) { // In Queue or Processing
                setTimeout(fetchSubmission.bind(null, submission_token), check_timeout);
                return;
            }
            handleResult(data);
        },
        error: handleRunError
    });
}

function changeEditorLanguage() {
    monaco.editor.setModelLanguage(sourceEditor.getModel(), $selectLanguage.find(":selected").attr("mode"));
    currentLanguageId = parseInt($selectLanguage.val());
    $(".lm_title")[0].innerText = fileNames[currentLanguageId];
    apiUrl = resolveApiUrl($selectLanguage.val());
}

function insertTemplate() {
    currentLanguageId = parseInt($selectLanguage.val());
    sourceEditor.setValue(sources[currentLanguageId]);
    stdinEditor.setValue(inputs[currentLanguageId] || "");
    $compilerOptions.val(compilerOptions[currentLanguageId] || "");
    changeEditorLanguage();
}

function loadRandomLanguage() {
    var values = [];
    for (var i = 0; i < $selectLanguage[0].options.length; ++i) {
        values.push($selectLanguage[0].options[i].value);
    }
    // $selectLanguage.dropdown("set selected", values[Math.floor(Math.random() * $selectLanguage[0].length)]);
    $selectLanguage.dropdown("set selected", values[19]);
    apiUrl = resolveApiUrl($selectLanguage.val())
    insertTemplate();
}

function resizeEditor(layoutInfo) {
    if (editorMode != "normal") {
        var statusLineHeight = $("#editor-status-line").height();
        layoutInfo.height -= statusLineHeight;
        layoutInfo.contentHeight -= statusLineHeight;
    }
}

function disposeEditorModeObject() {
    try {
        editorModeObject.dispose();
        editorModeObject = null;
    } catch(ignorable) {
    }
}

function changeEditorMode() {
    disposeEditorModeObject();

    if (editorMode == "vim") {
        editorModeObject = MonacoVim.initVimMode(sourceEditor, $("#editor-status-line")[0]);
    } else if (editorMode == "emacs") {
        var statusNode = $("#editor-status-line")[0];
        editorModeObject = new MonacoEmacs.EmacsExtension(sourceEditor);
        editorModeObject.onDidMarkChange(function(e) {
          statusNode.textContent = e ? "Mark Set!" : "Mark Unset";
        });
        editorModeObject.onDidChangeKey(function(str) {
          statusNode.textContent = str;
        });
        editorModeObject.start();
    }
}

function resolveLanguageId(id) {
    id = parseInt(id);
    return languageIdTable[id] || id;
}

function resolveApiUrl(id) {
    id = parseInt(id);
    return languageApiUrlTable[id] || defaultUrl;
}

function editorsUpdateFontSize(fontSize) {
    sourceEditor.updateOptions({fontSize: fontSize});
    stdinEditor.updateOptions({fontSize: fontSize});
    stdoutEditor.updateOptions({fontSize: fontSize});
}

function updateScreenElements() {
    var display = window.innerWidth <= 1200 ? "none" : "";
    $(".wide.screen.only").each(function(index) {
        $(this).css("display", display);
    });
}

setInterval(() => {
    userCode = document.getElementById('user-code');
    userCode.value = sourceEditor.getValue();
}, 500)

$(window).resize(function() {
    layout.updateSize();
    updateScreenElements();
    showMessages();
});

$(document).ready(function () {
    updateScreenElements();

    console.log("Hey, Judge0 IDE is open-sourced: https://github.com/judge0/ide. Have fun!");

    $selectLanguage = $("#select-language");
    $selectLanguage.change(function (e) {
        if (!isEditorDirty) {
            insertTemplate();
        } else {
            changeEditorLanguage();
        }
    });

    $compilerOptions = $("#compiler-options");
    $commandLineArguments = $("#command-line-arguments");
    $commandLineArguments.attr("size", $commandLineArguments.attr("placeholder").length);

    $insertTemplateBtn = $("#insert-template-btn");
    $insertTemplateBtn.click(function (e) {
        if (isEditorDirty && confirm("Are you sure? Your current changes will be lost.")) {
            insertTemplate();
        }
    });

    $runBtn = $("#run-btn");
    $runBtn.click(function (e) {
        run();
    });

    $navigationMessage = $("#navigation-message span");
    $updates = $("#judge0-more");

    $(`input[name="editor-mode"][value="${editorMode}"]`).prop("checked", true);
    $("input[name=\"editor-mode\"]").on("change", function(e) {
        editorMode = e.target.value;
        localStorageSetItem("editorMode", editorMode);

        resizeEditor(sourceEditor.getLayoutInfo());
        changeEditorMode();

        sourceEditor.focus();
    });

    $statusLine = $("#status-line");

    $(document).on("keydown", "body", function (e) {
        var keyCode = e.keyCode || e.which;
        if (keyCode == 120) { // F9
            e.preventDefault();
            run();
        } else if (keyCode == 119) { // F8
            e.preventDefault();
            var url = prompt("Enter URL of Judge0 API:", apiUrl);
            if (url != null) {
                url = url.trim();
            }
            if (url != null && url != "") {
                apiUrl = url;
                localStorageSetItem("api-url", apiUrl);
            }
        } else if (keyCode == 118) { // F7
            e.preventDefault();
            wait = !wait;
            localStorageSetItem("wait", wait);
            alert(`Submission wait is ${wait ? "ON. Enjoy" : "OFF"}.`);
        } else if (event.ctrlKey && keyCode == 107) { // Ctrl++
            e.preventDefault();
            fontSize += 1;
            editorsUpdateFontSize(fontSize);
        } else if (event.ctrlKey && keyCode == 109) { // Ctrl+-
            e.preventDefault();
            fontSize -= 1;
            editorsUpdateFontSize(fontSize);
        }
    });

    $("select.dropdown").dropdown();
    $(".ui.dropdown").dropdown();
    $(".ui.dropdown.site-links").dropdown({action: "hide", on: "hover"});
    $(".ui.checkbox").checkbox();
    $(".message .close").on("click", function () {
        $(this).closest(".message").transition("fade");
    });

    loadMessages();

    require(["vs/editor/editor.main", "monaco-vim", "monaco-emacs"], function (ignorable, MVim, MEmacs) {
        layout = new GoldenLayout(layoutConfig, $("#site-content"));

        MonacoVim = MVim;
        MonacoEmacs = MEmacs;

        layout.registerComponent("source", function (container, state) {
            sourceEditor = monaco.editor.create(container.getElement()[0], {
                automaticLayout: true,
                theme: "vs-dark",
                scrollBeyondLastLine: true,
                readOnly: state.readOnly,
                language: "cpp",
                minimap: {
                    enabled: false
                }
            });

            changeEditorMode();

            sourceEditor.getModel().onDidChangeContent(function (e) {
                currentLanguageId = parseInt($selectLanguage.val());
                isEditorDirty = sourceEditor.getValue() != sources[currentLanguageId];
            });

            sourceEditor.onDidLayoutChange(resizeEditor);
        });

        layout.registerComponent("stdin", function (container, state) {
            stdinEditor = monaco.editor.create(container.getElement()[0], {
                automaticLayout: true,
                theme: "vs-dark",
                scrollBeyondLastLine: false,
                readOnly: state.readOnly,
                language: "plaintext",
                minimap: {
                    enabled: false
                }
            });
        });

        layout.registerComponent("stdout", function (container, state) {
            stdoutEditor = monaco.editor.create(container.getElement()[0], {
                automaticLayout: true,
                theme: "vs-dark",
                scrollBeyondLastLine: false,
                readOnly: state.readOnly,
                language: "plaintext",
                minimap: {
                    enabled: false
                }
            });

            container.on("tab", function(tab) {
                tab.element.append("<span id=\"stdout-dot\" class=\"dot\" hidden></span>");
                tab.element.on("mousedown", function(e) {
                    e.target.closest(".lm_tab").children[3].hidden = true;
                });
            });
        });

        layout.on("initialised", function () {
            $(".monaco-editor")[0].appendChild($("#editor-status-line")[0]);
            if (getIdFromURI()) {
                loadSavedSource();
            } else {
                loadRandomLanguage();
            }
            $("#site-navigation").css("border-bottom", "1px solid black");
            sourceEditor.focus();
            editorsUpdateFontSize(fontSize);
        });

        layout.init();
    });
});

// Template Sources
var pythonSource = "print(\"hello, world\")";

var sources = {
    70: pythonSource,
    71: pythonSource,
};

var fileNames = {
    70: "script.py",
    71: "script.py",
};

var languageIdTable = {
    1001: 1,
    1002: 2,
    1003: 3,
    1004: 4,
    1005: 5,
    1006: 6,
    1007: 7,
    1008: 8,
    1009: 9,
    1010: 10,
    1011: 11,
    1012: 12,
    1013: 13,
    1014: 14,
    1015: 15,
    1021: 21,
    1022: 22,
    1023: 23,
    1024: 24
}

var extraApiUrl = "https://extra-ce.judge0.com";
var languageApiUrlTable = {
    1001: extraApiUrl,
    1002: extraApiUrl,
    1003: extraApiUrl,
    1004: extraApiUrl,
    1005: extraApiUrl,
    1006: extraApiUrl,
    1007: extraApiUrl,
    1008: extraApiUrl,
    1009: extraApiUrl,
    1010: extraApiUrl,
    1011: extraApiUrl,
    1012: extraApiUrl,
    1013: extraApiUrl,
    1014: extraApiUrl,
    1015: extraApiUrl,
    1021: extraApiUrl,
    1022: extraApiUrl,
    1023: extraApiUrl,
    1024: extraApiUrl
}

var competitiveProgrammingInput = "\
3\n\
3 2\n\
1 2 5\n\
2 3 7\n\
1 3\n\
3 3\n\
1 2 4\n\
1 3 7\n\
2 3 1\n\
1 3\n\
3 1\n\
1 2 4\n\
1 3\n\
";

var inputs = {
    54: competitiveProgrammingInput
}

var competitiveProgrammingCompilerOptions = "-O3 --std=c++17 -Wall -Wextra -Wold-style-cast -Wuseless-cast -Wnull-dereference -Werror -Wfatal-errors -pedantic -pedantic-errors";

var compilerOptions = {
    54: competitiveProgrammingCompilerOptions
}
