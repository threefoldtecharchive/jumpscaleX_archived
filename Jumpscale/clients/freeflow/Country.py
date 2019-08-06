class Country(object):
    COUNTRIES = {
        "Afghanistan": "AF",
        "Aland Islands": "AX",
        "Albania": "AL",
        "Algeria": "DZ",
        "American Samoa": "AS",
        "Andorra": "AD",
        "Angola": "AO",
        "Anguilla": "AI",
        "Antarctica": "AQ",
        "Antigua &amp; Barbuda": "AG",
        "Argentina": "AR",
        "Armenia": "AM",
        "Aruba": "AW",
        "Australia": "AU",
        "Austria": "AT",
        "Azerbaijan": "AZ",
        "Bahamas": "BS",
        "Bahrain": "BH",
        "Bangladesh": "BD",
        "Barbados": "BB",
        "Belarus": "BY",
        "Belgium": "BE",
        "Belize": "BZ",
        "Benin": "BJ",
        "Bermuda": "BM",
        "Bhutan": "BT",
        "Bolivia": "BO",
        "Bosnia &amp; Herzegovina": "BA",
        "Botswana": "BW",
        "Bouvet Island": "BV",
        "Brazil": "BR",
        "British Indian Ocean Territory": "IO",
        "British Virgin Islands": "VG",
        "Brunei": "BN",
        "Bulgaria": "BG",
        "Burkina Faso": "BF",
        "Burundi": "BI",
        "Cambodia": "KH",
        "Cameroon": "CM",
        "Canada": "CA",
        "Cape Verde": "CV",
        "Caribbean Netherlands": "BQ",
        "Cayman Islands": "KY",
        "Central African Republic": "CF",
        "Chad": "TD",
        "Chile": "CL",
        "China": "CN",
        "Christmas Island": "CX",
        "Cocos (Keeling) Islands": "CC",
        "Colombia": "CO",
        "Comoros": "KM",
        "Congo ": "CD",
        "Cook Islands": "CK",
        "Costa Rica": "CR",
        "Côte d’Ivoire": "CI",
        "Croatia": "HR",
        "Cuba": "CU",
        "Curaçao": "AN",
        "Cyprus": "CY",
        "Czechia": "CZ",
        "Denmark": "DK",
        "Djibouti": "DJ",
        "Dominica": "DM",
        "Dominican Republic": "DO",
        "Ecuador": "EC",
        "Egypt": "EG",
        "Equatorial Guinea": "GQ",
        "Eritrea": "ER",
        "Estonia": "EE",
        "Ethiopia": "ET",
        "Falkland Islands": "FK",
        "Faroe Islands": "FO",
        "Fiji": "FJ",
        "Finland": "FI",
        "France": "FR",
        "French Guiana": "GF",
        "French Polynesia": "PF",
        "French Southern Territories": "TF",
        "Gabon": "GA",
        "Gambia": "GM",
        "Georgia": "GE",
        "Germany": "DE",
        "Ghana": "GH",
        "Gibraltar": "GI",
        "Greece": "GR",
        "Greenland": "GL",
        "Grenada": "GD",
        "Guadeloupe": "GP",
        "Guam": "GU",
        "Guatemala": "GT",
        "Guernsey": "GG",
        "Guinea": "GW",
        "Guyana": "GY",
        "Haiti": "HT",
        "Heard &amp; McDonald Islands": "HM",
        "Honduras": "HN",
        "Hong Kong SAR China": "HK",
        "Hungary": "HU",
        "Iceland": "IS",
        "India": "IN",
        "Indonesia": "ID",
        "Iran": "IR",
        "Iraq": "IQ",
        "Ireland": "IE",
        "Isle of Man": "IM",
        "Israel": "IL",
        "Italy": "IT",
        "Jamaica": "JM",
        "Japan": "JP",
        "Jersey": "JE",
        "Jordan": "JO",
        "Kazakhstan": "KZ",
        "Kenya": "KE",
        "Kiribati": "KI",
        "Kosovo": "XK",
        "Kuwait": "KW",
        "Kyrgyzstan": "KG",
        "Laos": "LA",
        "Latvia": "LV",
        "Lebanon": "LB",
        "Lesotho": "LS",
        "Liberia": "LR",
        "Libya": "LY",
        "Liechtenstein": "LI",
        "Lithuania": "LT",
        "Luxembourg": "LU",
        "Macau SAR China": "MO",
        "Macedonia": "MK",
        "Madagascar": "MG",
        "Malawi": "MW",
        "Malaysia": "MY",
        "Maldives": "MV",
        "Mali": "ML",
        "Malta": "MT",
        "Marshall Islands": "MH",
        "Martinique": "MQ",
        "Mauritania": "MR",
        "Mauritius": "MU",
        "Mayotte": "YT",
        "Mexico": "MX",
        "Micronesia": "FM",
        "Moldova": "MD",
        "Monaco": "MC",
        "Mongolia": "MN",
        "Montenegro": "ME",
        "Montserrat": "MS",
        "Morocco": "MA",
        "Mozambique": "MZ",
        "Myanmar (Burma)": "MM",
        "Namibia": "NA",
        "Nauru": "NR",
        "Nepal": "NP",
        "Netherlands": "NL",
        "New Caledonia": "NC",
        "New Zealand": "NZ",
        "Nicaragua": "NI",
        "Niger": "NE",
        "Nigeria": "NG",
        "Niue": "NU",
        "Norfolk Island": "NF",
        "North Korea": "KP",
        "Northern Mariana Islands": "MP",
        "Norway": "NO",
        "Oman": "OM",
        "Pakistan": "PK",
        "Palau": "PW",
        "Palestinian Territories": "PS",
        "Panama": "PA",
        "Papua New Guinea": "PG",
        "Paraguay": "PY",
        "Peru": "PE",
        "Philippines": "PH",
        "Pitcairn Islands": "PN",
        "Poland": "PL",
        "Portugal": "PT",
        "Puerto Rico": "PR",
        "Qatar": "QA",
        "Réunion": "RE",
        "Romania": "RO",
        "Russia": "RU",
        "Rwanda": "RW",
        "Samoa": "WS",
        "San Marino": "SM",
        "São Tomé &amp; Príncipe": "ST",
        "Saudi Arabia": "SA",
        "Senegal": "SN",
        "Serbia": "RS",
        "Seychelles": "SC",
        "Sierra Leone": "SL",
        "Singapore": "SG",
        "Sint Maarten": "SX",
        "Slovakia": "SK",
        "Slovenia": "SI",
        "Solomon Islands": "SB",
        "Somalia": "SO",
        "South Africa": "ZA",
        "South Georgia &amp; South Sandwich Islands": "GS",
        "South Korea": "KR",
        "South Sudan": "SS",
        "Spain": "ES",
        "Sri Lanka": "LK",
        "St. Barthélemy": "BL",
        "St. Helena": "SH",
        "St. Kitts &amp; Nevis": "KN",
        "St. Lucia": "LC",
        "St. Martin": "MF",
        "St. Pierre &amp; Miquelon": "PM",
        "St. Vincent &amp; Grenadines": "VC",
        "Sudan": "SD",
        "Suriname": "SR",
        "Svalbard &amp; Jan Mayen": "SJ",
        "Swaziland": "SZ",
        "Sweden": "SE",
        "Switzerland": "CH",
        "Syria": "SY",
        "Taiwan": "TW",
        "Tajikistan": "TJ",
        "Tanzania": "TZ",
        "Thailand": "TH",
        "Timor": "TL",
        "Togo": "TG",
        "Tokelau": "TK",
        "Tonga": "TO",
        "Trinidad &amp; Tobago": "TT",
        "Tunisia": "TN",
        "Turkey": "TR",
        "Turkmenistan": "TM",
        "Turks &amp; Caicos Islands": "TC",
        "Tuvalu": "TV",
        "U.S. Outlying Islands": "UM",
        "U.S. Virgin Islands": "VI",
        "Uganda": "UG",
        "Ukraine": "UA",
        "United Arab Emirates": "AE",
        "United Kingdom": "GB",
        "United States": "US",
        "Uruguay": "UY",
        "Uzbekistan": "UZ",
        "Vanuatu": "VU",
        "Vatican City": "VA",
        "Venezuela": "VE",
        "Vietnam": "VN",
        "Wallis &amp; Futuna": "WF",
        "Western Sahara": "EH",
        "Yemen": "YE",
        "Zambia": "ZM",
        "Zimbabwe": "ZW",
    }

    @staticmethod
    def get_code(country):
        if country is None:
            return None
        if country not in Country.COUNTRIES:
            raise j.exceptions.Base("Unrecognized country")
        return Country.COUNTRIES[country]
