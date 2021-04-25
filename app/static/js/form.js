//
// Js functions to install components and process a crud form
//

function install_form() {
    _install_form($(".form-editor"));
}

function process_form(form) {
    var param = {"valid": true}, fieldset = form.children("fieldset");
    _process(param, fieldset, fieldset.attr("name"));
    debug(param);
    return param;
}

function _install_form(container) {
    //
    // Install array add or delete action
    //
    // Array add
    container.find(".act > .add").click(function () {
        // Find the last .list-group-item and clone it
        var list = $(this).parent().prev(".list-group"),
            template = list.children(".list-group-item.template"),
            clone = template.clone(true);
        clone.removeClass("template");
        list.append(clone);

        // Install components
        _install_components(clone);
    });
    // Array delete
    container.find(".act > .del").click(function () {
        var con = window.confirm("Are you sure to delete this item?");
        if (!con) {
            return false;
        }
        $(this).closest(".list-group-item").remove();
    });
    //
    // Install components
    //
    _install_components(container);
}

// Install components
// NOTE: Only install on the non-template inputs, for dynamic created inputs, need to invoke install_plupload manually
function _install_components(container) {
    container.find(".form-group").each(function (fgi, fgn) {
        var formGroup = $(fgn);

        // Skip form-groups in template
        if (formGroup.closest(".list-group-item").is(".template")) {
            return false;
        }
        if (formGroup.closest("fieldset").is(".template")) {
            return false;
        }

        // Lazy load images
        formGroup.find("img[data-src]").each(function (i, n) {
            var btn = $(n).closest(".plupload-input-group").children(".plupload");
            if (btn) {
                var preview = btn.attr("data-preview") ? JSON.parse(btn.attr("data-preview")) : {};
                $(n).attr("src", my_preview($(n).data("src"), preview));
            }
        });

        // Switch
        // https://getbootstrap.com/docs/4.5/components/forms/#switches
        formGroup.find(".custom-switch").each(function (i, n) {
            var id = "switch-" + my_random();
            var btn = $(n).find(":checkbox");
            btn.attr("id", id);
            btn.next("label").attr("for", id)
        });

        // Flatpickr
        // https://flatpickr.js.org/formatting/
        formGroup.find("input.date-time").each(function (i, n) {
            $(n).flatpickr({
                //locale: "zh",
                enableTime: true,
                dateFormat: "Y-m-d H:i:S",
                defaultHour: new Date().getHours(),
                defaultMinute: new Date().getMinutes()
            })
        });
        formGroup.find("input.date").each(function (i, n) {
            $(n).flatpickr({
                //locale: "zh",
                dateFormat: "Y-m-d"
            })
        });

        // Time range
        formGroup.find(".time-range-input-group").each(function (i, n) {
            var start = $(n).find(".time-start").timepicker({
                timeFormat: "H:i"
            });
            var end = $(n).find(".time-end").timepicker({
                timeFormat: "H:i"
            });
            start.change(function () {
                var val = $(this).val();
                if (!my_validateHhMm(val)) {
                    return false;
                }
                var tokens = val.split(":");
                var nextHour = (parseInt(tokens[0]) + 1).toString().padStart(2, "0");
                end.val(nextHour + ":" + tokens[1]);
            });
        });

        // Select2
        // https://select2.org/
        formGroup.find("select.select2").each(function (i, n) {
            var option = {
                containerCssClass: n.getAttribute("class").replace("select2", ""), // Remove class select2 as it impacts display
                dropdownAutoWidth: true,
                dropdownCssClass: n.classList.contains("custom-select-sm") || n.classList.contains("form-control-sm") ? "dropdown-menu dropdown-menu-sm show" : "dropdown-menu show",
                dropdownParent: n.closest('.modal-body') || document.body,
                tags: $(n).is("[tags]")
            };
            $(n).select2(option);
        });

        // Plupload
        // https://www.plupload.com/docs/v2/Getting-Started
        formGroup.find(".plupload").each(function (i, n) {
            install_plupload($(n));
        });

        // Rte
        // https://github.com/quilljs/quill/
        formGroup.find(".quill").each(function (i, n) {
            install_quill($(n));
        });
    });
}

var global_pluploading = false;

function install_plupload(btn) {
    var result = btn.closest(".plupload-input-group").find(".plupload-input-result"),
        multi = btn.is("[multiple]"),
        hiddens = btn.data("hiddens"),
        upload = btn.data("upload"),
        token = btn.data("token"),
        max = btn.data("max"),
        preview = btn.attr("data-preview") ? JSON.parse(btn.attr("data-preview")) : {},
        suffix = btn.attr("data-suffix") ? JSON.parse(btn.attr("data-suffix")) : {},
        filters = btn.attr("data-filters") ? JSON.parse(btn.attr("data-filters")) : {};
    var isImageResult = result.is(".image-input-result");
    // Generate a unique id for button so it can work correctly
    btn.attr("id", "plupload-" + my_random());
    var uploader = new plupload.Uploader({
        browse_button: btn[0],
        url: upload,
        max_file_size: max,
        filters: filters,
        multi_selection: multi,
        multipart_params: {token: token}
    });
    uploader.init();
    uploader.bind('FilesAdded', function (up, files) {
        var html = '';
        plupload.each(files, function (file) {
            if (isImageResult) {
                html += '<div id="' + file.id + '" class="image uploading"><div class="progress progress-sm"><div class="progress-bar" style="width:5%;"></div></div></div>'
            } else {
                html += '<div id="' + file.id + '" class="file uploading d-flex justify-content-start align-items-center"><div class="mr-3">' + file.name + '</div><div class="flex-grow-1 mr-3"><div class="progress progress-sm"><div class="progress-bar" style="width:5%;"></div></div></div></div>'
            }
        });
        if (multi) {
            result.append(html);
        } else {
            result.html(html);
        }
        up.start();
        global_pluploading = true;
    });
    uploader.bind('UploadProgress', function (up, file) {
        $("#" + file.id).find(".progress-bar").css("width", file.percent + "%");
    });
    uploader.bind('Error', function (up, err) {
        // Errors may happen before FilesAdded event, e.g, "File size error.", so need to check if any wrap div here
        if (err.file && $("#" + err.file.id).length) {
            var html = '<small class="text-danger">' + err.file.name + (isImageResult ? '<br>' : '') + err.message + ' (' + err.code + ')</small>';
            $("#" + err.file.id).removeClass("uploading").addClass("error").html(html);
        } else {
            showError("Failed when uploading, " + err.message + " (" + err.code + ")");
        }
    });
    uploader.bind("FileUploaded", function (up, file, c) {
        // Response from qiniu or local upload service
        var d = jQuery.parseJSON(c.response);
        // Service error, // https://developer.qiniu.com/kodo/manual/1651/simple-response
        if (d.error) {
            var html = '<small class="text-danger">' + file.name + (isImageResult ? '<br>' : '') + d.error + '</small>';
            $("#" + file.id).removeClass("uploading").addClass("error").html(html);
        } else {
            // Defined response, https://developer.qiniu.com/kodo/manual/1654/response-body
            // d
            //   url - uploaded url = base + '/' + key, e.g, //cdn.flask-seed.com/20200521/183247_821388.jpg
            //   key - relative path from base, e.g, 20200521/183247_821388.jpg
            //   name - upload file name
            //   width - image width, int
            //   height - image height, int
            var uploaded = $("#" + file.id);
            uploaded.removeClass("uploading").addClass("uploaded");
            if (isImageResult) {
                var src = my_preview(d.url, preview);
                var img = $('<img>').one("load", function () {
                    $(this).closest(".image").css("width", "auto");
                }).attr("src", src);
                uploaded.html(img);
                var btns = '<div class="btns"><a href="' + d.url + '" target="_blank">i</a><a href="javascript:;" onclick="$(this).closest(\'.image\').remove();">x</a></div>';
                uploaded.append(btns);
            } else {
                uploaded.find(".flex-grow-1").remove();
                var btns = '<div><a class="mr-2" href="' + d.url + '" target="_blank">i</a><a href="javascript:;" onclick="$(this).closest(\'.file\').remove();">x</a></div>';
                uploaded.append(btns);
            }
            $.each(hiddens.split(','), function (i, k) {
                var v = k in d ? d[k] : "";
                if (k == "url") {
                    v = my_preview(v, suffix);
                }
                var hidden = $('<input type="hidden" name="' + k + '">').val(v);
                uploaded.append(hidden);
            });
        }
    });
    uploader.bind("UploadComplete", function (up, files) {
        global_pluploading = false;
    });
}

function install_quill(div) {
    var random = my_random(),
        upload = div.data("upload"),
        token = div.data("token"),
        max = div.data("max"),
        preview = div.attr("data-preview") ? JSON.parse(div.attr("data-preview")) : {},
        filters = div.attr("data-filters") ? JSON.parse(div.attr("data-filters")) : {};
    div.attr("id", "quill-" + random);
    // Install quill
    var toolbarOptions = [
        [{'header': [2, false]}],
        ['bold', 'italic', 'underline'],
        [{'list': 'ordered'}, {'list': 'bullet'}],
        ['link', 'image'],
        ['blockquote', 'code-block'],
        ['clean']
    ];
    var quill = new Quill(div[0], {
            placeholder: 'Please input rich text here',
            theme: 'snow',
            modules: {
                toolbar: {
                    container: toolbarOptions,
                    handlers: {
                        'image': function (value) {
                            if (value) {
                                $("#quill-plupload-" + random).next(".moxie-shim").children("input[type=file]").trigger('click');
                            } else {
                                this.quill.format('image', false);
                            }
                        }
                    }
                },
            }
        }
    );
    // Install plupload for quill
    var pluploaBtn = div.closest(".rte-input-group").find(".quill-plupload");
    pluploaBtn.attr("id", "quill-plupload-" + random);
    var uploader = new plupload.Uploader({
        browse_button: pluploaBtn[0],
        url: upload,
        max_file_size: max,
        filters: filters,
        multi_selection: true,
        multipart_params: {token: token}
    });
    uploader.init();
    uploader.bind('FilesAdded', function (up, files) {
        up.start();
        global_pluploading = true;
    });
    uploader.bind('Error', function (up, err) {
        if (err.file) {
            showError("Failed when uploading file " + err.file.name + ", " + err.message + " (" + err.code + ")");
        } else {
            showError("Failed when uploading, " + err.message + " (" + err.code + ")");
        }
    });
    uploader.bind("FileUploaded", function (up, file, c) {
        var d = jQuery.parseJSON(c.response);
        if (d.error) {
            showError("Failed when uploading file " + file.name + ", " + d.error);
        } else {
            var length = (quill.getSelection() || {}).index || quill.getLength();
            quill.insertEmbed(length, 'image', my_preview(d.url, preview));
            quill.insertText(length + 1, '\n');
            quill.setSelection(length + 2);
        }
    });
    uploader.bind("UploadComplete", function (up, files) {
        global_pluploading = false;
    });
}

function _process(param, field, path) {
    debug("Try to process path " + path);
    // object
    if (field.is(".object")) {
        field.find("> .form-group, > .form-row .form-group, > fieldset").each(function (i, n) {
            var name = $(n).attr("name");
            if (name) {
                if (name.includes(".")) { // Restart path, so that more than two models can be posted together
                    _process(param, $(n), name);
                } else {
                    _process(param, $(n), path + "." + name);
                }
            }
        });
    }
    // array
    else if (field.is(".array")) {
        var select = field.find("select"), pluploadInputGroup = field.find(".plupload-input-group");
        if (select.length) { // array of integer/number/string
            select.removeClass("is-valid is-invalid");
            var vals = select.val();
            if (vals.length) {
                $.each(vals, function (i, n) {
                    param[path + "[" + i + "]"] = n;
                });
            } else {
                // Manually validate required
                if (select.is("[required]")) {
                    select.addClass("is-invalid");
                    param["valid"] = false;
                }
            }
            debug("Parsed array's length is " + vals.length);
        } else if (pluploadInputGroup.length) { // array of string/object
            pluploadInputGroup.removeClass("is-valid is-invalid");
            var uploads = pluploadInputGroup.find(".uploaded");
            if (uploads.length) {
                $.each(uploads, function (i, n) {
                    var hiddens = $(n).find(":hidden[name]");
                    if (hiddens.length == 1) {
                        param[path + "[" + i + "]"] = hiddens.val();
                    } else {
                        $.each(hiddens, function (j, h) {
                            param[path + "[" + i + "]." + $(h).attr("name")] = $(h).val();
                        });
                    }
                });
            } else {
                // Manually validate required
                if (pluploadInputGroup.is("[required]")) {
                    pluploadInputGroup.addClass("is-invalid");
                    param["valid"] = false;
                }
            }
            debug("Parsed array's length is " + uploads.length);
        } else {
            field.find("> .list-group > .list-group-item").not(".template").each(function (i, n) {
                _process(param, $(n).children(), path + "[" + i + "]");
            });
        }
    }
    // simple types
    else {
        var radioInputGroup = field.find(".radio-input-group"),
            pluploadInputGroup = field.find(".plupload-input-group"),
            rteInputGroup = field.find(".rte-input-group"),
            timeRangeInputGroup = field.find(".time-range-input-group"),
            inputGroup = field.find(".input-group"),
            simpleInput = field.find(":input[name]");
        if (radioInputGroup.length) {
            radioInputGroup.removeClass("is-valid is-invalid");
            // If radio group is in array, they may share same name, so here use the active button to get checked value
            var active = radioInputGroup.find(".active");
            if (active.length) {
                param[path] = active.children(":radio").val().trim();
            } else {
                // Manually validate required
                if (radioInputGroup.is("[required]")) {
                    radioInputGroup.addClass("is-invalid");
                    param["valid"] = false;
                }
            }
        } else if (pluploadInputGroup.length) {
            pluploadInputGroup.removeClass("in-valid is-invalid");
            var upload = pluploadInputGroup.find(".uploaded");
            if (upload.length) {
                param[path] = upload.find(":hidden[name=url]").val();
            } else {
                // Manually validate required
                if (pluploadInputGroup.is("[required]")) {
                    pluploadInputGroup.addClass("is-invalid");
                    param["valid"] = false;
                }
            }
        } else if (rteInputGroup.length) {
            rteInputGroup.removeClass("in-valid is-invalid");
            var html = rteInputGroup.find(".ql-editor").html().trim(),
                text = rteInputGroup.find(".ql-editor").text().trim();
            if (text.length) {
                param[path] = html;
            } else {
                // Manually validate required
                if (rteInputGroup.is("[required]")) {
                    rteInputGroup.addClass("is-invalid");
                    param["valid"] = false;
                }
            }
        } else if (timeRangeInputGroup.length) {
            var inputStart = timeRangeInputGroup.find("input.time-start"), start = inputStart.val().trim(),
                inputEnd = timeRangeInputGroup.find("input.time-end"), end = inputEnd.val().trim();
            timeRangeInputGroup.removeClass("in-valid is-invalid");
            inputStart.removeClass("in-valid is-invalid");
            inputEnd.removeClass("in-valid is-invalid");
            if (start.length || end.length) {
                param[path.replace("@", inputStart.attr("name"))] = start;
                param[path.replace("@", inputEnd.attr("name"))] = end;
                param[path] = start + "~" + end; // Path with placeholder for debug
                if (!my_validateHhMm(start) || !my_validateHhMm(end) || start >= end) {
                    timeRangeInputGroup.addClass("is-invalid");
                    inputStart.addClass("is-invalid");
                    inputEnd.addClass("is-invalid");
                    param["valid"] = false;
                } else {
                    timeRangeInputGroup.addClass("is-valid");
                    inputStart.addClass("is-valid");
                    inputEnd.addClass("is-valid");
                }
            } else {
                if (timeRangeInputGroup.is("[required]")) {
                    timeRangeInputGroup.addClass("is-invalid");
                    inputStart.addClass("is-invalid");
                    inputEnd.addClass("is-invalid");
                    param["valid"] = false;
                }
            }
        } else if (inputGroup.length) {
            var innerInput = inputGroup.find(":input[name]");
            inputGroup.removeClass("is-invalid is-valid");
            var val = innerInput.val().trim();
            if (innerInput.is(":checkbox")) {
                val = innerInput.is(":checked") ? "true" : "false";
            }
            if (val.length) {
                param[path] = val;
                // Invoke built-in validation for Non-empty value
                if (innerInput[0].checkValidity) {
                    if (innerInput[0].checkValidity() === false) {
                        inputGroup.addClass("is-invalid");
                        innerInput.addClass("is-invalid");
                        param["valid"] = false;
                    } else {
                        inputGroup.addClass("is-valid");
                        innerInput.addClass("is-valid");
                    }
                }
            } else {
                // Manually validate required only for empty value
                if (inputGroup.is("[required]")) {
                    inputGroup.addClass("is-invalid");
                    innerInput.addClass("is-invalid");
                    param["valid"] = false;
                }
            }
        } else if (simpleInput.length) {
            simpleInput.removeClass("is-invalid is-valid");
            var val = simpleInput.val().trim();
            if (simpleInput.is(":checkbox")) {
                val = simpleInput.is(":checked") ? "true" : "false";
            }
            if (val.length) {
                param[path] = val;
                // Invoke built-in validation for Non-empty value
                if (simpleInput[0].checkValidity) {
                    if (simpleInput[0].checkValidity() === false) {
                        simpleInput.addClass("is-invalid");
                        param["valid"] = false;
                    } else {
                        simpleInput.addClass("is-valid");
                    }
                }
            } else {
                // Manually validate required only for empty value
                if (simpleInput.is("[required]")) {
                    simpleInput.addClass("is-invalid");
                    param["valid"] = false;
                }
            }
        }
        debug("Parsed string is " + param[path]); // All values in form are string type
        if (path.includes("@")) { // Remove paths with placeholder
            delete param[path]
        }
    }
}

function debug(msg, more) {
    if (console && console.log) {
        if (more) {
            console.log(msg, more)
        } else {
            console.log(msg);
        }
    }
}

function my_preview(url, config) {
    var rawUrl = url.split(/[#?]/)[0];
    var ext = rawUrl.split('.').pop().trim().toLowerCase();
    var isVideo = (ext == "mov" || ext == "mp4" || ext == "mpeg" || ext == "webm") ? true : false;
    if (isVideo && "video" in config) {
        return rawUrl + config["video"];
    } else if ("image" in config) {
        return rawUrl + config["image"];
    } else {
        return url;
    }
}

function my_random() {
    return Math.floor((Math.random() * 1000000000));
}

function my_validateHhMm(val) {
    return /^([0-1]?[0-9]|2[0-4]):([0-5][0-9])(:[0-5][0-9])?$/.test(val);
}