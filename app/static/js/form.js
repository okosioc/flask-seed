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
// NOTE: Only install on the visible inputs, for dynamic created inputs, need to invoke install_plupload manually
function _install_components(container) {
    // Flatpickr
    // https://flatpickr.js.org/formatting/
    container.find("input.date-time:visible").each(function (i, n) {
        $(n).flatpickr({
            enableTime: true,
            dateFormat: "Y-m-d H:i:S",
            defaultHour: new Date().getHours(),
            defaultMinute: new Date().getMinutes()
        })
    });
    container.find("input.date:visible").each(function (i, n) {
        $(n).flatpickr({
            dateFormat: "Y-m-d"
        })
    });

    // Select2
    // https://select2.org/
    container.find("select.select2:visible").each(function (i, n) {
        var option = {tags: $(n).is("[tags]")};
        $(n).select2(option)
    });

    // Image
    // https://www.plupload.com/docs/v2/Getting-Started
    container.find(".plupload:visible").each(function (i, n) {
        install_plupload($(n));
    });

    // Rte
    // https://github.com/quilljs/quill/
    container.find(".quill:visible").each(function (i, n) {
        install_quill($(n));
    });
}

var global_pluploading = false;

function install_plupload(btn) {
    var result = btn.closest(".image-input-group").find(".image-input-result"),
        multi = btn.is("[multiple]"),
        hiddens = btn.data("hiddens"),
        upload = btn.data("upload"),
        token = btn.data("token"),
        max = btn.data("max"),
        preview = btn.data("preview"),
        filters = btn.data("filters");
    // Generate a unique id for button so it can work correctly
    btn.attr("id", "plupload-" + Math.round(new Date() / 1000));

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
            html += '<div id="' + file.id + '" class="image uploading"><div class="progress progress-sm"><div class="progress-bar" style="width:5%;"></div></div></div>';
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
        if (err.file) {
            var html = '<small class="text-danger">' + err.file.name + '<br>' + err.message + ' (' + err.code + ')</small>';
            // Errors may happen before FilesAdded event, e.g, "File size error.", so need to check if any wrap div here
            if ($("#" + err.file.id).length) {
                $("#" + err.file.id).removeClass("uploading").addClass("error").html(html);
            } else {
                html = '<div id="' + err.file.id + '" class="image error">' + html + '</div>';
                result.html(html);
            }
        } else {
            showError("Failed when uploading, " + err.message + " (" + err.code + ")");
        }
    });
    uploader.bind("FileUploaded", function (up, file, c) {
        // Response from qiniu service
        var d = jQuery.parseJSON(c.response);
        // Service error, // https://developer.qiniu.com/kodo/manual/1651/simple-response
        if (d.error) {
            var html = '<small class="text-danger">' + file.name + '<br>' + d.error + '</small>';
            $("#" + file.id).removeClass("uploading").addClass("error").html(html);
        }
        // Defined response, https://developer.qiniu.com/kodo/manual/1654/response-body
        // d
        //   url - uploaded url = base + '/' + key, e.g, //cdn.flask-seed.com/20200521/183247_821388.jpg
        //   key - relative path from base, e.g, 20200521/183247_821388.jpg
        //   name - upload file name
        //   width - image width, int
        //   height - image height, int
        else {
            var img = $('<img>').one("load", function () {
                $(this).closest(".image").css("width", "auto");
            }).attr("src", d.url + preview);
            var image = $("#" + file.id).removeClass("uploading").addClass("uploaded").html(img);
            var btns = '<div class="btns"><a href="' + d.url + '" target="_blank">i</a><a href="javascript:;" onclick="$(this).closest(\'.image\').remove();">x</a></div>';
            image.append(btns);
            $.each(hiddens.split(','), function (i, k) {
                var v = k in d ? d[k] : "";
                var hidden = $('<input type="hidden" name="' + k + '">').val(v);
                image.append(hidden);
            });
        }
    });
    uploader.bind("UploadComplete", function (up, files) {
        global_pluploading = false;
    });
}

function install_quill(div) {
    var random = Math.round(new Date() / 1000),
        upload = div.data("upload"),
        token = div.data("token"),
        max = div.data("max"),
        preview = div.data("preview"),
        filters = div.data("filters");
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
            quill.insertEmbed(length, 'image', d.url + preview);
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
        field.find("> .form-group, > fieldset").each(function (i, n) {
            _process(param, $(n), path + "." + $(n).attr("name"));
        });
    }
    // array
    else if (field.is(".array")) {
        var select = field.children("select"), imageInputGroup = field.children(".image-input-group");
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
        } else if (imageInputGroup.length) { // array of string/object
            imageInputGroup.removeClass("in-valid is-invalid");
            var images = imageInputGroup.find(".image.uploaded");
            if (images.length) {
                $.each(images, function (i, n) {
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
                if (imageInputGroup.is("[required]")) {
                    imageInputGroup.addClass("is-invalid");
                    param["valid"] = false;
                }
            }
            debug("Parsed array's length is " + images.length);
        } else {
            field.find("> .list-group > .list-group-item").not(".template").each(function (i, n) {
                _process(param, $(n).children(), path + "[" + i + "]");
            });
        }
    }
    // simple types
    else {
        var radioInputGroup = field.children(".radio-input-group"),
            imageInputGroup = field.children(".image-input-group"),
            rteInputGroup = field.children(".rte-input-group"),
            simpleInput = field.children(":input[name]");
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
        } else if (imageInputGroup.length) {
            imageInputGroup.removeClass("in-valid is-invalid");
            var image = imageInputGroup.find(".image.uploaded");
            if (image.length) {
                param[path] = image.find(":hidden[name=url]").val();
            } else {
                // Manually validate required
                if (imageInputGroup.is("[required]")) {
                    imageInputGroup.addClass("is-invalid");
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
        } else if (simpleInput.length) {
            simpleInput.removeClass("is-invalid is-valid");
            var val = simpleInput.val().trim();
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