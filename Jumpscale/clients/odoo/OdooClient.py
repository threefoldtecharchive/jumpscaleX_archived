from Jumpscale import j

try:
    import erppeek

except:
    j.builders.runtimes.python.pip_package_install("ERPpeek")
    import erppeek


JSConfigBase = j.application.JSBaseConfigClass


class OdooClient(JSConfigBase):
    _SCHEMATEXT = """
    @url = jumpscale.odoo.client
    name* = "main" (S)
    host = "127.0.0.1" (S)
    port = "8069"
    login_admin="admin" (S)
    password_ = "admin" (S)
    database = "odoo_test" (S)
    """

    def _init(self, **kwargs):
        self._client = None

    @property
    def client(self):
        if not self._client:
            self._client = erppeek.Client(
                "http://{}:{}".format(self.host, self.port),
                db=self.database,
                user=self.login_admin,
                password=self.password_,
            )
        return self._client

    def module_install(self, module_name):
        return self.client.install(module_name)

    def module_remove(self, module_name):
        return self.client.uninstall(module_name)

    def modules_default_install(self):

        modules = [
            "crm",
            "website",
            "project",
            "stock",
            # "account",
            # "stock_account",
            "sale_management",
            "crm_project",
            "website_crm",
            "website_sale",
            # "purchase",
            # "purchase_stock",
            "hr",
            "hr_recruitment",
            "hr_expense",
            # "analytic",
            "auth_signup",
            # "barcodes",
            "board",
            "contacts",
            "crm_livechat",
            # "digest",
            "document",
            "event",
            "event_sale",
            # "fetchmail",
            "hr_contract",
            "hr_holidays",
            "l10n_be",
            "l10n_multilang",
            "mail",
            "mail_bot",
            # "partner_autocomplete",
            "product",
            "rating",
            "sale",
            "sale_crm",
            "sale_expense",
            "sale_purchase",
            # "sale_stock",
            "sales_team",
            "sms",
            "social_media",
            "survey_crm",
            "web",
            "web_diagram",
            "web_editor",
            "web_kanban_gauge",
            "web_settings_dashboard",
            "web_tour",
            "web_unsplash",
            "website_event_sale",
            "website_form",
            "website_form_project",
            "website_livechat",
            "website_mail",
            "website_partner",
            "website_payment",
            "website_rating",
            "website_sale_management",
            "website_sale_stock",
            "website_survey",
            "website_theme_install",
            "survey",
            "lunch",
            "calendar",
            "website_blog",
            "website_hr_recruitment",
            "website_slides",
            "website_forum",
            "fleet",
            "website_event",
            "im_livechat",
            "theme_bootswatch",
            "portal",
            "note_pad",
            "note",
            "google_account",
            "google_calendar",
            "google_drive",
            "google_spreadsheet",
            "hr_expense_check",
            "hr_org_chart",
            "hr_recruitment_survey",
            "hr_timesheet_attendance",
            "mass_mailing_crm",
            "mass_mailing_event",
            "mass_mailing_event_track",
            "mass_mailing_sale",
            "membership",
            "website_customer",
            "website_event_questions",
            "website_event_track",
            "website_google_map",
            "website_hr",
            "website_links",
            "website_membership",
        ]

        # modules = [
        #     # "expenses",
        #     # "dashboards",
        #     "contacts",
        #     # "leaves",
        #     # "discuss",
        #     "lunch",
        #     "maintenance",
        #     # "slides",
        #     # "blogs",
        #     "calendar",
        #     "fleet",
        #     # "events",
        #     "crm",
        #     "crm_livechat",
        #     "crm_project",
        #     "web",
        #     "portal",
        #     "website",
        #     "project",
        #     "crm",
        #     # "employees",
        #     # "inventory",
        #     # "invoicing",
        #     # "sales",
        #     # "nodes",
        #     # "ecommerce",
        #     # "purchase",
        #     # "recruitment",
        # ]
        for module in modules:
            self.module_install(module)

    def user_add(self, username, password):
        new_user = self.client.model("res.users").create({"login": username, "name": username})
        new_user.password = password
        return new_user

    def user_delete(self, user, password):
        user_id = self.client.login(user, password)
        user = self.client.model("res.users").get(user_id)
        self.client.login(self.login_admin, self.password_)
        return user.unlink()

    def login(self, user, password):
        return self.client.login(user, password)

    def databases_list(self):
        return self.client.db.list()
