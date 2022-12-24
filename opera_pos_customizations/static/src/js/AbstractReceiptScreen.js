odoo.define('opera_pos_customizations.AbstractReceiptScreen', function (require) {
    'use strict';

    const AbstractReceiptScreen = require('point_of_sale.AbstractReceiptScreen');
    const Registries = require('point_of_sale.Registries');

    const AbstractReceiptScreenExtend = AbstractReceiptScreen => class extends AbstractReceiptScreen {
    
        async _printWeb() {
            try {
                const isPrinted = document.execCommand('print', false, null);
                if (!isPrinted)  setTimeout(function(){
                    window.print();
                }, 500);

                return true;
            } catch (err) {
                await this.showPopup('ErrorPopup', {
                    title: this.env._t('Printing is not supported on some browsers'),
                    body: this.env._t(
                        'Printing is not supported on some browsers due to no default printing protocol ' +
                            'is available. It is possible to print your tickets by making use of an IoT Box.'
                    ),
                });
                return false;
            }
        }
    }

    Registries.Component.extend(AbstractReceiptScreen , AbstractReceiptScreenExtend);

    return AbstractReceiptScreen;
});
