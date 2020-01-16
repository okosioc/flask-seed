// Components
!function ($) {
    "use strict";

    var Components = function () {
    };

    // Initialize tooltip
    Components.prototype.initTooltipPlugin = function () {
        $.fn.tooltip && $('[data-toggle="tooltip"]').tooltip()
    },

        // Initialize popover
        Components.prototype.initPopoverPlugin = function () {
            $.fn.popover && $('[data-toggle="popover"]').popover()
        },

        // Initialize toast
        Components.prototype.initToastPlugin = function () {
            $.fn.toast && $('[data-toggle="toast"]').toast()
        },

        // Initialize Slimscroll
        Components.prototype.initSlimScrollPlugin = function () {
            //You can change the color of scroll bar here
            $.fn.slimScroll && $(".slimscroll").slimScroll({
                height: 'auto',
                position: 'right',
                size: "8px",
                touchScrollStep: 20,
                color: '#9ea5ab'
            });
        },

        // Initialize
        Components.prototype.init = function () {
            this.initTooltipPlugin(),
                this.initPopoverPlugin(),
                this.initToastPlugin(),
                this.initSlimScrollPlugin();
        }, $.Components = new Components, $.Components.Constructor = Components

}(window.jQuery),

    // App
    function ($) {
        'use strict';

        var App = function () {
            this.$body = $('body'), this.$window = $(window);
        };

        // Initialize
        App.prototype.init = function () {
            $.Components.init();
        }, $.App = new App, $.App.Constructor = App

    }(window.jQuery),

    // Initialize main application module
    function ($) {
        "use strict";
        $.App.init();
    }(window.jQuery);

// Waves Effect
Waves.init();