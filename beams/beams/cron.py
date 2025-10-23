import frappe
from frappe.utils import now

def send_escalation_notifications():
    hd_settings = frappe.get_doc("HD Settings")
    if hd_settings.enable_escalation_notifications:
        # Response Due Escalations
        response_due_tickets = frappe.get_all("HD Ticket", filters={
            "response_due_escalation_send": 0,
            "first_responded_on": ("is", "not set"),
            "response_by": ("<", now())
        }, fields=["name", "agent_group"])
        for ticket_data in response_due_tickets:
            team = frappe.get_doc("HD Team", ticket_data.agent_group)
            if team.escalation_to:
                ticket = frappe.get_doc("HD Ticket", ticket_data.name)
                frappe.sendmail(
                    recipients=team.escalation_to,
                    subject=f"Response Due for Ticket #{ticket.name}",
                    message=frappe.render_template(hd_settings.response_due_template, {"doc": ticket}),
                    now=True
                )
                frappe.db.set_value("HD Ticket", ticket.name, "response_due_escalation_send", 1)

        # Resolution Due Escalations
        resolution_due_tickets = frappe.get_all("HD Ticket", filters={
            "resolution_due_escalation_send": 0,
            "resolution_date": ("is", "not set"),
            "resolution_by": ("<", now())
        }, fields=["name", "agent_group"])
        for ticket_data in resolution_due_tickets:
            team = frappe.get_doc("HD Team", ticket_data.agent_group)
            if team.escalation_to:
                ticket = frappe.get_doc("HD Ticket", ticket_data.name)
                frappe.sendmail(
                    recipients=team.escalation_to,
                    subject=f"Resolution Due for Ticket #{ticket.name}",
                    message=frappe.render_template(hd_settings.resolution_due_template, {"doc": ticket}),
                    now=True
                )
                frappe.db.set_value("HD Ticket", ticket.name, "resolution_due_escalation_send", 1)
