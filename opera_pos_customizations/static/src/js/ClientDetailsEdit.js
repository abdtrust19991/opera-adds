odoo.define('opera_pos_customizations.ClientDetailsEdit', function(require) {
    'use strict';

    const ClientDetailsEdit = require('point_of_sale.ClientDetailsEdit');
    const Registries = require('point_of_sale.Registries');

    const ClientDetailsEditExtend = ClientDetailsEdit => class extends ClientDetailsEdit {

        saveChanges() {
            let processedChanges = {};
            for (let [key, value] of Object.entries(this.changes)) {
                if (this.intFields.includes(key)) {
                    processedChanges[key] = parseInt(value) || false;
                } else {
                    processedChanges[key] = value;
                }
            }
            if ((!this.props.partner.phone && !processedChanges.phone) || processedChanges.phone === '' ){
                return this.showPopup('ErrorPopup', {
                  title: _('A Customer Phone Is Required'),
                });
            }

            var phone = processedChanges.phone;
            if (phone){

                if (phone.length !== 11){
                    return this.showPopup('ErrorPopup', {
                      title: _('A Customer Phone Is Invalid'),
                    });
                }

                let partners = this.env.pos.db.search_partner(phone.trim());
                if (partners.length){
                    return this.showPopup('ErrorPopup', {
                      title: _('A Customer Phone Is Already Exist'),
                    });
                }

            }

            super.saveChanges()
        }

    }

    Registries.Component.extend(ClientDetailsEdit , ClientDetailsEditExtend);

    return ClientDetailsEdit;
});
