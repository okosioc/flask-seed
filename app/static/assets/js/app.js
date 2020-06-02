//
// Init
//
(function ($) {

    'use strict';

    function initComponents() {
        // Bootstrap tooltip
        $('[data-toggle="tooltip"]').tooltip();
        // Bootstrap popover
        $('[data-toggle="popover"]').popover();
        // Slimscroll - scroll content within a container
        $(".slimscroll").slimScroll({
            height: 'auto',
            position: 'right',
            size: "8px",
            touchScrollStep: 20,
            color: '#9ea5ab'
        });
    }

    function initToast() {
        function toast(msg, type) {
            $.notify({
                message: msg
            }, {
                type: type,
                allow_dismiss: true,
                placement: {
                    from: "top",
                    align: "center"
                },
                offset: {
                    x: 20,
                    y: 80
                },
                spacing: 10,
                template: '<div data-notify="container" class="col-6 alert alert-{0}" role="alert">' +
                '<button type="button" aria-hidden="true" class="close" data-notify="dismiss">×</button>' +
                '<span data-notify="icon"></span>' +
                '<span data-notify="title">{1}</span>' +
                '<span data-notify="message">{2}</span>' +
                '<div class="progress" data-notify="progressbar">' +
                '<div class="progress-bar progress-bar-{0}" role="progressbar" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100" style="width: 0%;"></div>' +
                '</div>' +
                '<a href="{3}" target="{4}" data-notify="url"></a>' +
                '</div>'
            });
        }

        window.showError = function (msg) {
            toast(msg, "danger");
        };

        window.showInfo = function (msg) {
            toast(msg, "info");
        };

        window.showSuccess = function (msg) {
            toast(msg, "success");
        };

        window.showWarning = function (msg) {
            toast(msg, "warning");
        };

        window.coming = function () {
            showInfo("Coming soon!");
        };
    }

    function initScroll2Top() {
        $(window).scroll(function () {
            ($(window).scrollTop() > 300) ? $("a#scroll-to-top").addClass('visible') : $("a#scroll-to-top").removeClass('visible');
        });

        $("a#scroll-to-top").click(function () {
            $("html, body").animate({scrollTop: 0}, "slow");
            return false;
        });
    }


    function init() {
        initComponents();

        // Toast
        initToast();

        // Scroll to tup
        initScroll2Top();

        // Wave effects
        Waves.init();
    }

    init();

})(window.jQuery);