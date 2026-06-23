frappe.ui.form.on("Licence", {
	setup(frm) {
		frm.set_query("licence_type", () => ({
			filters: { applies_to: ["in", ["Licence", "All"]], disabled: 0 },
		}));
	},
	refresh(frm) {
		if (frm.doc.expiry_date && frm.doc.status !== "Expired") {
			const days = frappe.datetime.get_day_diff(frm.doc.expiry_date, frappe.datetime.now_date());
			if (days < 0) {
				frm.dashboard.set_headline_alert(__("This licence expired {0} day(s) ago.", [Math.abs(days)]));
			} else if (days <= 30) {
				frm.dashboard.set_headline_alert(__("Expires in {0} day(s).", [days]));
			}
		}
	},
});
