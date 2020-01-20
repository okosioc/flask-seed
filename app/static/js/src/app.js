//
// Init
//
(function ($) {

    'use strict';

    function initComponents() {
        $('[data-toggle="tooltip"]').tooltip();
        $('[data-toggle="popover"]').popover();
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
            // TODO
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

        // Scroll to tup
        initScroll2Top();

        // Wave effects
        Waves.init();
    }

    init();

})(window.jQuery);