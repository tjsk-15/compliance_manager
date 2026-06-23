frappe.ui.form.on("Insurance Policy", {
	setup(frm) {
		frm.set_query("insurance_type", () => ({
			filters: { applies_to: ["in", ["Insurance", "All"]], disabled: 0 },
		}));
	},
	refresh(frm) {
		if (frm.doc.expiry_date && frm.doc.status !== "Expired") {
			const days = frappe.datetime.get_day_diff(frm.doc.expiry_date, frappe.datetime.now_date());
			if (days < 0) {
				frm.dashboard.set_headline_alert(__("This policy expired {0} day(s) ago.", [Math.abs(days)]));
			} else if (days <= 30) {
				frm.dashboard.set_headline_alert(__("Expires in {0} day(s).", [days]));
			}
		}
	},
});
