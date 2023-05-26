//
// Js functions to install components and process a crud form
//

function install_form() {
    $(".form-editor").each(function (i, n) {
        _install_form($(n));
    })
    $(".form-query").each(function (i, n) {
        _install_components($(n));
    })
}

function process_form(form) {
    var param = {"valid": true}, fieldset = form.find("> fieldset, > .card > div > fieldset");
    _process(param, fieldset, fieldset.attr("name"));
    debug(param);
    return param;
}

function _install_form(container) {
    //
    // Install components
    //
    _install_components(container);
}

//
// Array actions in .array
//

/**
 * Add array item directly.
 */
function array_action_add(btn) {
    // Find the template and append clone one before it
    var template = btn.closest("fieldset.array").find(".array-item.template");
    var clone = template.clone(true);
    clone.removeClass("template");
    clone.insertBefore(template);
    template.next(".array-item").hide(); // Hide empty alert
    // Install components
    _install_components(clone);
}

/**
 * Delete array item.
 */
function array_action_delete(btn) {
    var title = btn.attr("data-title");
    var msg = "确定删除此" + title + "么?";
    var con = window.confirm(msg);
    if (!con) {
        return false;
    }
    var template = btn.closest("fieldset.array").find(".array-item.template");
    if (template.prevAll(".array-item").length == 1) {
        template.next(".array-item").show(); // Show empty alert
    }
    btn.closest(".array-item").remove();
}

/**
 * Show array item modal.
 * e.g:
 *   - arrays are in modal format, when we need to edit we need to show corresponding modal
 */
function array_action_show_modal(btn) {
    var items = btn.closest(".array-item").prevAll(".array-item");
    var index = items.length;
    var modals = btn.closest("fieldset.array").find(".modals > .modal");
    var modal = $(modals.get(index));
    if (!modal.attr("id")) {
        modal.attr("id", "modal-" + my_random());
    }
    modal.modal('show');
}

/**
 * Clone template modal, but not create corresponding item.
 */
function array_action_add_modal(btn) {
    // Find the template and append clone one before it
    var template = btn.closest("fieldset.array").find(".modals > .modal.template");
    var clone = template.clone(true);
    clone.removeClass("template").addClass("adding");
    clone.insertBefore(template);
    clone.attr("id", "modal-" + my_random());
    // Install components
    _install_components(clone);
    //
    clone.modal("show");
}

/**
 * Cancel modal.
 */
function array_action_cancel_modal(btn) {
    var modal = btn.closest(".modal");
    modal.modal("hide");
    if (modal.is(".adding")) {
        modal.remove();
    }
}

/**
 * Save array item.
 * e.g,
 *   - arrays are in modal format, when we save in modal, we need to redraw the content of table
 */
function array_action_save_modal(btn) {
    var modal = btn.closest(".modal");
    var param = {"valid": true}, fieldset = modal.find(".modal-body > fieldset"), fieldset_name = fieldset.attr("name");
    _process(param, fieldset, fieldset_name);
    debug(param);
    if (!param["valid"]) {
        showError('检测到不正确的数据, 请更正后重试!');
        return false;
    }
    // Convert legacy post params to object, i.e, {user.name:x, user.phone:x}
    var object = {};
    $.each(param, function (k, v) {
        object[k.replace(fieldset_name + '.', '')] = v;
    })
    debug(object);
    var items = btn.closest("fieldset.array").find(".array-item[name]");
    var item = null;
    if (modal.is(".adding")) { // Adding
        var item_template = items.last();
        var item_clone = item_template.clone(true);
        item_clone.removeClass("template");
        item_clone.insertBefore(item_template);
        render_template_using_object(item_clone, object);
        item_clone.show();
        item = item_clone;
        item_template.next(".array-item").hide(); // Hide empty alert row
        modal.removeClass("adding");
    } else { // Editing
        var index = modal.prevAll(".modal").length;
        item = $(items.get(index));
        render_template_using_object(item, object);
    }
    modal.modal("hide");
}

/**
 * Delete item together with corresponding modal.
 */
function array_action_delete_modal(btn) {
    var title = btn.attr("data-title");
    var msg = "确定删除此" + title + "么?";
    var con = window.confirm(msg);
    if (!con) {
        return false;
    }
    var items = btn.closest("fieldset.array").find(".array-item[name]");
    if (items.length == 2) { // Show empty alert row
        items.last().next(".array-item").show();
    }
    var item = btn.closest(".array-item");
    var index = item.prevAll(".array-item").length;
    var modals = btn.closest("fieldset.array").find(".modals > .modal");
    item.remove();
    $(modals.get(index)).remove();
}

/**
 * Show search modal.
 */
// {key:[]}
var relation_action_search_records = {};

function relation_action_show_search_modal(btn) {
    // Mark searching
    $(".searching").removeClass("searching");
    btn.addClass("searching");
    //
    var modal = $("#search-" + btn.attr("relation-key"));
    modal.modal("show");
}

/**
 * Search related models in modal.
 */
function relation_action_search(btn, page) {
    if (btn.is(".doing")) {
        return;
    }
    var modal = btn.closest(".modal");
    var url = modal.attr("relation-url");
    var key = modal.attr("relation-key");
    //
    var param = {"p": page};
    modal.find(".form-search :input[name]").each(function () {
        param[$(this).attr("name")] = $(this).val();
    });
    //
    btn.addClass("doing");
    var method = btn.is("input") ? "val" : "text";
    var oldLabel = btn[method]();
    btn[method](oldLabel + "...");
    //
    $.post(url, param, function (result) {
        if (result.error == 0) {
            // response json format: {error, message, ${key}, pagination}
            relation_action_render_results(key, result[key], result.pagination);
        } else {
            showError(result.message);
        }
        btn.removeClass("doing");
        btn[method](oldLabel);
    }, "json");
}

/**
 * Render search results into table in modal.
 */
function relation_action_render_results(key, results, pagination) {
    var modal = $("#search-" + key.replace(/_/g, '-'));
    var key = modal.attr("relation-key");
    var id = modal.attr("relation-id");
    //
    var table = modal.find("table");
    var rows = table.find("tbody > tr[name]");
    var row_template = rows.last();
    row_template.prevAll("tr").remove(); // Reset existing rows
    // add rows
    relation_action_search_records[key] = results;
    $.each(results, function (i, v) {
        var row = row_template.clone(true);
        row.removeClass("template");
        row.insertBefore(row_template);
        render_template_using_object(row, v, key, id);
        row.show();
    });
    if (results.length) {
        row_template.next("tr").hide(); // Hide info row
    } else {
        row_template.next("tr").show(); // Show info row
    }
    //
    var pagination = pagination, ul = table.next(".pagination");
    ul.html(""); // Reset existing pagination
    if (pagination.pages > 1) {
        // pagination example: iter_pages: [1, 2], next: 2, page: 1, pages: 2, prev: null}
        if (pagination.prev) {
            ul.append('<li class="page-item"><a class="page-link" href="javascript:;" onclick="relation_action_search($(this), ' + pagination.prev + ')"><</a></li>');
        }
        $.each(pagination.iter_pages, function (i, p) {
            if (p && p == pagination.page) {
                ul.append('<li class="page-item active"><a class="page-link" href="javascript:;">' + p + '<span class="sr-only">(current)</span></a></li>');
            } else if (p) {
                ul.append('<li class="page-item"><a class="page-link" href="javascript:;" onclick="relation_action_search($(this), ' + p + ')">' + p + '</a></li>');
            } else {
                ul.append('<li class="page-item"><a class="page-link" href="javascript:;">...</a></li>');
            }
        });
        if (pagination.next) {
            ul.append('<li class="page-item"><a class="page-link" href="javascript:;" onclick="relation_action_search($(this), ' + pagination.next + ')">></a></li>');
        }
        ul.show();
    } else {
        ul.hide();
    }
}

/**
 * Reset search contidion in search modal.
 */
function relation_action_search_reset(btn) {
    btn.closest(".form-search").find(":input[name]").val("");
}

/**
 * Checkbox changed event in search modal.
 */
function relation_action_checkbox_changed(btn) {
    var table = btn.closest("table");
    var checkboxes = table.find("tbody > tr[name]").not(".template").find(".list-checkbox");
    if (btn.is(".list-checkbox-all")) {
        var checked = btn.is(":checked");
        checkboxes.prop("checked", checked);
    } else {
        var checked = btn.is(":checked");
    }
    //
    var checked_length = checkboxes.filter(":checked").length;
    btn.closest(".modal-content").find(".modal-footer .span-checked").text(checked_length);
}

/**
 * Return selected related modals and render them.
 */
function relation_action_choosed_return(btn) {
    var modal = btn.closest(".modal");
    var key = modal.attr("relation-key");
    var title = modal.attr("relation-title");
    var id = modal.attr("relation-id");
    //
    var table = btn.closest(".modal-content").find(".modal-body table");
    var checked = table.find("tbody > tr[name]").not(".template").find(".list-checkbox:checked");
    if (checked.length == 0) {
        showError(btn.attr("message"));
        return false;
    }
    // Callback
    var checked_ids = $.map(checked, function (v) {
        return $(v).attr("id").replace(key + "-", ""); // checkbox id is set in render_results
    });
    var checked_objects = relation_action_search_records[key].filter(function (v) {
        return checked_ids.includes(String(v[id]))
    });
    //
    var trigger = $(".searching");
    var fieldset = trigger.closest("fieldset.relation");
    var return_type = trigger.attr("relation-return"); // many or one
    if (return_type == "one" && checked_objects.length > 1) {
        showError("只能选择一个" + trigger.attr("data-title") + "!");
        return false;
    }
    //
    var relationInputGroup = fieldset.find(".form-group > .relation-input-group"),
        items = fieldset.find(".array-item[name]");
    if (relationInputGroup.length) {
        var existing = relationInputGroup.children(".badge");
        if (return_type == "one") {
            existing.remove();
        }
        $.each(checked_objects, function (i, object) {
            relationInputGroup.append('<span class="font-size-base badge badge-soft-secondary mr-2" data-id="' + object[id] + '">' + object[title] + '<small class="fe fe-x ml-2" style="cursor:pointer" onclick="$(this).parent().remove();"></small></span>')
        });
    } else if (items.length) {
        var item_template = items.last();
        var modals = fieldset.find(".modals > .modal");
        var modal_template = modals.last();
        $.each(checked_objects, function (i, object) {
            var item = item_template.clone(true);
            item.removeClass("template");
            item.insertBefore(item_template);
            render_template_using_object(item, object, key, id);
            item.show();
            item_template.next(".array-item").hide(); // Hide empty alert row
            //
            var modal = modal_template.clone(true);
            modal.removeClass("template show");
            modal.insertBefore(modal_template);
            render_template_using_object(modal, object, key, id);
            modal.attr("id", "modal-" + my_random());
        });
    }
    //
    var search = btn.closest(".search-modal");
    search.modal("hide");
}

/**
 * Render template using object.
 *
 * relation_key and relation_key are used to set the id to checkbox
 */
function render_template_using_object(template, object, relation_key, relation_id) {
    // Render each field in template
    template.find("[name]").each(function (i, n) {
        var field = $(n);
        // Prevent fieldset and form-group that having names
        if (field.is("fieldset") || field.is(".form-group")) {
            return true;
        }
        var name = field.attr("name"), format = field.attr("format"),
            enum_type = field.attr("enum");
        //
        var value = object[name];
        // debug(`Try to update field with name ${name} format ${format}: ${value}`);
        //
        function parse_value(v) {
            if (enum_type) {
                if (v) {
                    v = global_enums[enum_type][v];
                }
            } else if (["checkbox", "switch"].includes(format)) {
                v = (v == "true" ? "是" : "否");
            } else if (format == 'datetime') {
                if (v) {
                    v = v.substr(0, 19); //
                }
            } else if (["text", "int", "float"].includes(format)) {
                var content = field.children();
                if (content.length > 0) { // If is html template
                    content = content.clone(true);
                    if (content.is(".avatar")) {
                        var title = content.find(".avatar-title");
                        if (v) {
                            title.text(v[0]);
                        } else {
                            title.text("");
                        }
                    } else if (content.is(".progress")) {
                        var bar = content.find(".progress-bar");
                        if (v) {
                            bar.css("width", "" + v + "%").attr("aria-valuenow", v);
                        } else {
                            bar.css("width", "0%").attr("aria-valuenow", "0");
                        }
                    } else {
                        content.text("UNSUPPORTED!");
                    }
                    return content;
                }
            } else if (['avatar', 'image'].includes(format)) {
                var content = field.children().clone(true);
                var image = content.find("img");
                var span = image.next("span[fallback]");
                if (v) {
                    image.removeClass("d-none").attr("src", v);
                    span.addClass("d-none").text("");
                } else {
                    image.addClass("d-none").attr("src", "");
                    span.removeClass("d-none").text(object[span.attr("fallback")][0]);
                }
                return content;
            } else if (format == 'link') {
                var content = field.children().clone(true);
                var link = content.find("a");
                if (v) {
                    link.attr("href", v);
                } else {
                    link.attr("href", "javascript:;");
                }
                return content;
            }
            return v || "-";
        }

        //
        if (Array.isArray(value)) {
            if (value.length) {
                // Array of object only display length
                if (typeof value[0] === 'object' && value[0] !== null) {
                    field.html(value.length);
                } else {
                    field.html(value.map(function (v) {
                        return parse_value(v);
                    }).join(" "));
                }
            } else {
                field.html("-");
            }
        } else if (typeof value === 'object' && value !== null) {
            var name_field = null;
            $.each(value, function (i, key) {
                if (key.match(/title|name|\w+name/i)) {
                    name_field = key;
                    return false;
                }
            });
            if (name_field) {
                value = value[name_field];
                field.html(value || "-");
            } else {
                field.html("-");
            }
        } else {
            if (field.is(':input')) {
                field.val(parse_value(value));
            } else {
                field.html(parse_value(value));
            }
        }
    });
    // Checkbox
    var checkbox = template.find(".list-checkbox");
    if (relation_id && checkbox.length) {
        checkbox.attr("id", relation_key + "-" + object[relation_id]);
        checkbox.next("label").attr("for", relation_key + "-" + object[relation_id]);
    }
}

function relation_action_search_reset(btn) {
    btn.closest(".form-search").find(":input[name]").val("");
}


//
// Input hook for link format
//
function external_link_open(btn) {
    var link = btn.closest(".input-group").find("input[name]").val().trim();
    if (link.length) {
        if (link.startsWith("http://") || link.startsWith("https://")) {
            window.open(link);
        } else {
            showWarning('Please input a valid link!')
        }
    }
}

// Install components
// NOTE: Only install on the non-template inputs, for dynamic created inputs, need to invoke _install_components manually
function _install_components(container) {
    container.find(".form-group").each(function (fgi, fgn) {
        var formGroup = $(fgn);

        // Skip form-groups in template
        if (formGroup.closest(".array-item").is(".template")) {
            return false;
        }
        if (formGroup.closest(".modal").is(".template")) {
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
                locale: "zh",
                allowInput: true,
                enableTime: true,
                dateFormat: "Y-m-d H:i:S",
                defaultHour: new Date().getHours(),
                defaultMinute: new Date().getMinutes()
            })
        });
        formGroup.find("input.date").each(function (i, n) {
            $(n).flatpickr({
                allowInput: true,
                locale: "zh",
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

        // Cascador
        formGroup.find('.cascader-input-group').each(function (i, n) {
            var $cascaderInput = $(n).find('.cascader');
            var $cascaderList = $(n).find(".cascader-list");
            var source = window[$cascaderInput.attr("data-source")];
            if (!source) {
                source = [];
            }
            $.each(source, function (i, l0) {
                var $li0 = null;
                if (l0.children && l0.children.length) {
                    $li0 = $('<li class="dropright"><a class="dropdown-item dropdown-toggle" href="javascript:;" data-toggle="dropdown" code="' + l0.code + '">' + l0.name + '</a></li>')
                    var $ul1 = $('<ul class="dropdown-menu"></ul>')
                    $.each(l0.children, function (j, l1) {
                        $ul1.append($('<li><a class="dropdown-item" href="javascript:;" code="' + l1.code + '">' + l1.name + '</a></li>'));
                    });
                    $li0.append($ul1);
                } else {
                    $li0 = $('<li><a class="dropdown-item" code="' + l0.code + '">' + l0.name + '</a></li>');
                }
                $cascaderList.append($li0);
            })
            // On click
            $cascaderList.find("a").click(function (e) {
                e.preventDefault();
                e.stopPropagation();
                var $a = $(this);
                var parentMenu = $a.closest('.dropdown-menu');
                // Deactive all sub menus
                var siblingSubMenus = parentMenu.find('.dropdown-menu');
                $.each(siblingSubMenus, function (i, n) {
                    $(n).removeClass("show");
                    $(n).find("a").removeClass("active");
                });
                // Deactive siblings a and active current a
                parentMenu.find("> li > a").removeClass("active");
                $a.addClass("active");
                // Set input value
                var names = [], codes = [];
                $a.parentsUntil(".cascader-list").each(function (i, n) {
                    if ($(n).is("li")) { // Every li has a, e.g, ul>li>ul>li>a
                        var $lia = $(n).find('> a');
                        names.push($lia.text());
                        codes.push($lia.attr("code"));
                    }
                });
                $cascaderInput.val(names.reverse().join('/'));
                $cascaderInput.attr("data-codes", JSON.stringify(codes.reverse()));
                // Show current sub menu
                var dropdown = $a.parent('.dropup, .dropright, .dropdown, .dropleft');
                if (dropdown.length) { // has sub menu, show it
                    // Active sub menu
                    var currentMenu = dropdown.find('.dropdown-menu');
                    currentMenu.addClass("show");
                } else { // leaf, hide the whole menu
                    $cascaderList.removeClass("show");
                }
            });
            // Init
            var codes = $cascaderInput.attr("data-codes") ? JSON.parse($cascaderInput.attr("data-codes")) : [];
            var names = [];
            var ul = $cascaderList;
            $.each(codes, function (i, n) {
                var li = ul.find("> li:has(a[code='" + codes[i] + "'])");
                if (li.length) {
                    var a = li.children("a");
                    a.addClass("active");
                    names.push(a.text());
                    ul = li.children("ul");
                    if (ul.length === 0) {
                        return false;
                    } else {
                        ul.addClass("show");
                    }
                }
            });
            $cascaderInput.val(names.join('/'));
        });

        // Tag Cloud, Tags + .Typeahead
        // https://github.com/corejavascript/typeahead.js
        formGroup.find(".tag-cloud-input-group").each(function (i, n) {
            var cloud = $(n);
            var tags = cloud.attr("data-tags") ? JSON.parse(cloud.attr("data-tags")) : [];
            var substringMatcher = function (strs) {
                return function findMatches(q, cb) {
                    var matches, substringRegex;
                    matches = [];
                    $.each(strs, function (i, str) {
                        if (str.includes(q)) {
                            matches.push(str);
                        }
                    });
                    cb(matches);
                };
            };
            var choosed = function (val) {
                val = $.trim(val);
                if (val.length > 0) {
                    var existings = cloud.children(".badge");
                    var found = false;
                    $.each(existings, function (i, n) {
                        var label = $.trim($(n).text());
                        if (label == val) {
                            found = true;
                            return false;
                        }
                    });
                    if (!found) {
                        var position = cloud.find(".twitter-typeahead");
                        position.before('<span class="font-size-base badge badge-soft-secondary mr-2 mb-2">' + val + '<small class="fe fe-x ml-2" style="cursor:pointer" onclick="$(this).parent().remove();"></small></span>');
                    } else {
                        showWarning("已经包含该标签!");
                    }
                }
            }
            cloud.find('.tag-input').typeahead({
                hint: false,
                highlight: true,
                minLength: 0
            }, {
                name: "tags",
                limit: 10,
                source: substringMatcher(tags),
            }).bind('typeahead:select', function (ev, suggestion, tag) {
                choosed(suggestion);
                $(this).typeahead("val", "").blur();
            }).on('keyup', function (e) {
                if (e.which == 13) {
                    choosed($(this).val());
                    $(this).typeahead("val", "").blur();
                }
            });
        });

        // ranger
        formGroup.find(".range-input-group").each(function (i, n) {
            var ranger = $(n).find(".custom-range");
            var range_value = $(n).find(".range-value");
            var value = range_value.text();
            // A mapping, Step => Value
            var steps = $(n).attr("data-steps") ? JSON.parse($(n).attr("data-steps")) : {};
            var max = -1;
            if (Object.keys(steps).length) {
                max = Object.keys(steps).length - 1;
                ranger.attr("max", max);
                // find step from value
                for (var step in steps) {
                    if (String(steps[step]) == value) {
                        ranger.val(parseInt(step));
                        break;
                    }
                }
            }
            ranger.on("input", function () {
                var step = String($(this).val());
                var value = step;
                if (max != -1) {
                    value = steps[step];
                }
                range_value.text(value);
            });
        });

        // Select2
        // https://select2.org/
        formGroup.find("select.select2").each(function (i, n) {
            var change_event = n.getAttribute("data-onchange");
            var option = {
                containerCssClass: n.getAttribute("class").replace("select2", ""), // Remove class select2 as it impacts display
                //dropdownAutoWidth: true,
                dropdownCssClass: n.classList.contains("custom-select-sm") || n.classList.contains("form-control-sm") ? "dropdown-menu dropdown-menu-sm show" : "dropdown-menu show",
                dropdownParent: n.closest('.modal-body') || document.body,
                tags: $(n).is("[tags]")
            };
            $(n).select2(option).on("select2:select", function (e) {
                if (change_event) {
                    window[change_event](e, n);
                }
            });
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

        // Autosize
        formGroup.find('.autosize').each(function (i, n) {
            autosize(n);
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
            var html = '<small class="text-danger">' + file.name + (isImageResult ? '<br>' : ' ') + d.error + '</small>';
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
        var card = field.children(".card");
        if (card.length) {
            field = card.children("div")
        }
        field.find(
            "> .form-group, " +
            "> .form-row .form-group, " +
            "> .row  > div > .form-group, " +
            "> .row  > div > .row  > div > .form-group, " +
            "> .row  > div > .card > div > .row  > div > .form-group, " +
            "> fieldset, " +
            "> .row  > div > fieldset, " +
            "> .row  > div > .card > div > fieldset, " +
            "> .row  > div > .card > div > .row  > div > fieldset"
        ).each(function (i, n) {
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
        var modals = field.find(".modals"),  // Array in modal/timeline/media format, using modal for really input
            items = field.find('.array-item[name]'), // Array in table/grid format and non-format
            select = field.find("select"),
            pluploadInputGroup = field.find(".plupload-input-group"),
            tagCloudInputGroup = field.find(".tag-cloud-input-group, .relation-input-group"),
            cascaderInputGroup = field.find(".cascader-input-group");
        if (modals.length) { // array of object in modal format
            modals.find("> .modal").not(".template").each(function (i, n) {
                var inner = $(n).find(".modal-body > fieldset");
                _process(param, inner, path + "[" + i + "]");
            });
        } else if (items.length) {
            items.not(".template").each(function (i, n) {
                // If is tr, is inline-table mode, each row contains td[name] with a form-control in it
                if ($(n).is("tr")) {
                    $(n).find("> td[name]").each(function (j, m) {
                        _process(param, $(m), path + "[" + i + "]." + $(m).attr("name"));
                    });
                }
                // Normal recrusive logic
                else {
                    var fieldset = $(n).find("fieldset[name]");
                    if (fieldset.length) {
                        _process(param, fieldset, path + "[" + i + "]");
                    } else {
                        // If not fieldset, should contain a simple field
                        var field = $(n).find(".form-group[name]");
                        if (field.length) {
                            _process(param, field, path + "[" + i + "]");
                        }
                    }
                }
            });
        } else if (select.length) { // array of relation/integer/number/string
            select.removeClass("is-valid is-invalid");
            var vals = select.val();
            if (vals.length) {
                if (field.is(".relation")) {
                    var id = field.children(".form-group").attr("relation-id");
                    var title = field.children(".form-group").attr("relation-title");
                    $.each(vals, function (i, n) {
                        param[path + "[" + i + "]." + id] = n;
                        param[path + "[" + i + "]." + title] = select.children("option[value=" + n + "]").text();
                    });
                } else {
                    $.each(vals, function (i, n) {
                        param[path + "[" + i + "]"] = n;
                    });
                }
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
        } else if (tagCloudInputGroup.length) { // array of string/relation in tag format
            tagCloudInputGroup.removeClass("is-valid is-invalid");
            var badges = tagCloudInputGroup.children(".badge");
            if (badges.length) {
                if (field.is(".relation")) {
                    var id = tagCloudInputGroup.parent(".form-group").attr("relation-id");
                    var title = tagCloudInputGroup.parent(".form-group").attr("relation-title");
                    $.each(badges, function (i, n) {
                        param[path.replace("@", "") + "[" + i + "]." + id] = $(n).attr("data-id");
                        param[path.replace("@", "") + "[" + i + "]." + title] = $.trim($(n).text());
                    });
                } else {
                    $.each(badges, function (i, n) {
                        param[path + "[" + i + "]"] = $.trim($(n).text());
                    });
                }
            } else {
                // Manually validate required
                if (tagCloudInputGroup.is("[required]")) {
                    tagCloudInputGroup.addClass("is-invalid");
                    param["valid"] = false;
                }
            }
            debug("Parsed array's length is " + badges.length);
        } else if (cascaderInputGroup.length) { // array of string/int in cascader format
            cascaderInputGroup.removeClass("is-valid is-invalid");
            var $cascaderInput = cascaderInputGroup.find(".cascader");
            var codes = $cascaderInput.attr("data-codes") ? JSON.parse($cascaderInput.attr("data-codes")) : [];
            if (codes.length) {
                $.each(codes, function (i, n) {
                    param[path + "[" + i + "]"] = n;
                });
            } else {
                // Manually validate required
                if (cascaderInputGroup.is("[required]")) {
                    cascaderInputGroup.addClass("is-invalid");
                    param["valid"] = false;
                }
            }
            debug("Parsed array's length is " + codes.length);
        } else {
            field.children("fieldset").not(".template").each(function (i, n) {
                _process(param, $(n), path + "[" + i + "]");
            });
        }
    }
    // simple types
    else {
        var radioInputGroup = field.find(".radio-input-group"),
            pluploadInputGroup = field.find(".plupload-input-group"),
            rteInputGroup = field.find(".rte-input-group"),
            timeRangeInputGroup = field.find(".time-range-input-group"),
            rangeInputGroup = field.find(".range-input-group"),
            relationInputGroup = field.find(".relation-input-group"),
            inputGroup = field.find(".input-group"),
            selectInput = field.find("select"),
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
        } else if (rangeInputGroup.length){
            rangeInputGroup.removeClass("in-valid is-invalid");
            var value = rangeInputGroup.find(".range-value").text().trim();
            if (value.length) {
                param[path] = value;
            } else {
                // Manually validate required
                if (rangeInputGroup.is("[required]")) {
                    rangeInputGroup.addClass("is-invalid");
                    param["valid"] = false;
                }
            }
        } else if (relationInputGroup.length) {
            relationInputGroup.removeClass("is-valid is-invalid");
            var badge = relationInputGroup.children(".badge");
            if (badge.length) {
                if (field.is(".relation")) {
                    var id = field.attr("relation-id");
                    var title = field.attr("relation-title");
                    param[path.replace("@", id)] = badge.attr("data-id");
                    param[path.replace("@", title)] = $.trim(badge.text());
                } else {
                    param[path] = $.trim(badge.text());
                }
            } else {
                // Manually validate required
                if (relationInputGroup.is("[required]")) {
                    relationInputGroup.addClass("is-invalid");
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
        } else if (selectInput.length) {
            selectInput.removeClass("is-invalid is-valid");
            var val = selectInput.val();
            if (val.length) {
                if (field.is(".relation")) {
                    var id = field.attr("relation-id");
                    var title = field.attr("relation-title");
                    param[path.replace("@", id)] = val;
                    param[path.replace("@", title)] = selectInput.children("option[value=" + val + "]").text();
                } else {
                    param[path] = val;
                }
            } else {
                if (selectInput.is("[required]")) {
                    selectInput.addClass("is-invalid");
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