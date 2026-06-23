frappe.ui.form.on("Compliance Record", {
	setup(frm) {
		frm.set_query("category", () => ({
			filters: { applies_to: ["in", ["Compliance", "All"]], disabled: 0 },
		}));
	},
	refresh(frm) {
		if (frm.doc.due_date && !["Completed"].includes(frm.doc.status)) {
			const days = frappe.datetime.get_day_diff(frm.doc.due_date, frappe.datetime.now_date());
			if (days < 0) {
				frm.dashboard.set_headline_alert(__("Overdue by {0} day(s).", [Math.abs(days)]));
			} else if (days <= 30) {
				frm.dashboard.set_headline_alert(__("Due in {0} day(s).", [days]));
			}
		}
	},
});
