frappe.ui.form.on("Trademark", {
	setup(frm) {
		frm.set_query("trademark_class", () => ({
			filters: { applies_to: ["in", ["Trademark", "All"]], disabled: 0 },
		}));
	},
	refresh(frm) {
		if (frm.doc.valid_till && frm.doc.status !== "Expired") {
			const days = frappe.datetime.get_day_diff(frm.doc.valid_till, frappe.datetime.now_date());
			if (days < 0) {
				frm.dashboard.set_headline_alert(__("This trademark expired {0} day(s) ago.", [Math.abs(days)]));
			} else if (days <= 30) {
				frm.dashboard.set_headline_alert(__("Valid for {0} more day(s).", [days]));
			}
		}
	},
});
