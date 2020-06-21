
#
# Data source: https://data.worldbank.org/indicator/SP.POP.TOTL
# Last updated 2018
# License : CC BY-4.0
#

def get_country_population(country):
    '''
    Returns country population in mn
    '''
    try:
        pop = country_data[country][1]
    except KeyError:
        pop = 0
    return round(pop / 1000000, 1)

def get_country_continent(country):
    try:
        con = continent[country_data[country][2]]
    except KeyError:
        con = "n/a"
    return con

country_data = {
"[World]": ["", 8065514043, ""],
"[North America]": ["", 909605388, ""],
"[Europe]": ["", 901718708, ""],
"[Asia]": ["", 4526007227, ""],
"[South America]": ["", 423558844, ""],
"[Africa]": ["", 1262842470, ""],
"[Ocenia]": ["", 41781406, ""],
"Afghanistan": ["AFG", 37172386, "AS"],
"Albania": ["ALB", 2866376, "EU"],
"Algeria": ["DZA", 42228429, "AF"],
"American Samoa": ["ASM", 55465, "OC"],
"Andorra": ["AND", 77006, "EU"],
"Angola": ["AGO", 30809762, "AF"],
"Antigua and Barbuda": ["ATG", 96286, "NA"],
"Argentina": ["ARG", 44494502, "SA"],
"Armenia": ["ARM", 2951776, "AS"],
"Aruba": ["ABW", 105845, "NA"],
"Australia": ["AUS", 24992369, "OC"],
"Austria": ["AUT", 8847037, "EU"],
"Azerbaijan": ["AZE", 9942334, "AS"],
"Bahamas": ["BHS", 385640, "NA"],
"Bahrain": ["BHR", 1569439, "AS"],
"Bangladesh": ["BGD", 161356039, "AS"],
"Barbados": ["BRB", 286641, "NA"],
"Belarus": ["BLR", 9485386, "EU"],
"Belgium": ["BEL", 11422068, "EU"],
"Belize": ["BLZ", 383071, "NA"],
"Benin": ["BEN", 11485048, "AF"],
"Bermuda": ["BMU", 63968, "NA"],
"Bhutan": ["BTN", 754394, "AS"],
"Bolivia": ["BOL", 11353142, "SA"],
"Bosnia and Herzegovina": ["BIH", 3323929, "EU"],
"Botswana": ["BWA", 2254126, "AF"],
"Brazil": ["BRA", 209469333, "SA"],
"British Virgin Islands": ["VGB", 29802, "NA"],
"Brunei": ["BRN", 428962, "AS"],
"Bulgaria": ["BGR", 7024216, "EU"],
"Burkina Faso": ["BFA", 19751535, "AF"],
"Burundi": ["BDI", 11175378, "AF"],
"Cabo Verde": ["CPV", 543767, "AF"],
"Cambodia": ["KHM", 16249798, "AS"],
"Cameroon": ["CMR", 25216237, "AF"],
"Canada": ["CAN", 37058856, "NA"],
"Cayman Islands": ["CYM", 64174, "NA"],
"Central African Republic": ["CAF", 4666377, "AF"],
"Chad": ["TCD", 15477751, "AF"],
"Channel Islands": ["CHI", 170499, "EU"],
"Chile": ["CHL", 18729160, "SA"],
"China": ["CHN", 1392730000, "AS"],
"Colombia": ["COL", 49648685, "SA"],
"Comoros": ["COM", 832322, "AF"],
"Congo (Kinshasa)": ["COD", 84068091, "AF"],
"Congo (Brazzaville)": ["COG", 5244363, "AF"],
"Costa Rica": ["CRI", 4999441, "NA"],
"Cote d'Ivoire": ["CIV", 25069229, "AF"],
"Croatia": ["HRV", 4089400, "EU"],
"Cuba": ["CUB", 11338138, "NA"],
"Curacao": ["CUW", 159849, "SA"],
"Cyprus": ["CYP", 1189265, "AS"],
"Czech Republic": ["CZE", 10625695, "EU"],
"Czechia": ["CZE", 10625695, "EU"],
"Denmark": ["", 5824857, "EU"],
"Djibouti": ["DJI", 958920, "AF"],
"Dominica": ["DMA", 71625, "NA"],
"Dominican Republic": ["DOM", 10627165, "NA"],
"Ecuador": ["ECU", 17084357, "SA"],
"Egypt": ["EGY", 98423595, "AF"],
"El Salvador": ["SLV", 6420744, "NA"],
"Equatorial Guinea": ["GNQ", 1308974, "AF"],
"Eritrea": ["", 5100000, "AF"],
"Estonia": ["EST", 1320884, "EU"],
"Eswatini": ["SWZ", 1136191, "AF"],
"Ethiopia": ["ETH", 109224559, "AF"],
"Faroe Islands": ["FRO", 48497, "EU"],
"Fiji": ["FJI", 883483, "OC"],
"Finland": ["FIN", 5518050, "EU"],
"France": ["FRA", 66987244, "EU"],
"French Polynesia": ["PYF", 277679, "OC"],
"Gabon": ["GAB", 2119275, "AF"],
"Gambia": ["GMB", 2280102, "AF"],
"Georgia": ["GEO", 3731000, "AS"],
"Germany": ["DEU", 82927922, "EU"],
"Ghana": ["GHA", 29767108, "AF"],
"Gibraltar": ["GIB", 33718, "EU"],
"Greece": ["GRC", 10727668, "EU"],
"Greenland": ["GRL", 56025, "NA"],
"Grenada": ["GRD", 111454, "NA"],
"Guam": ["GUM", 165768, "OC"],
"Guatemala": ["GTM", 17247807, "NA"],
"Guinea": ["GIN", 12414318, "AF"],
"Guinea-Bissau": ["GNB", 1874309, "AF"],
"Guyana": ["GUY", 779004, "SA"],
"Haiti": ["HTI", 11123176, "NA"],
"Honduras": ["HND", 9587522, "NA"],
"Hong Kong SAR, China": ["HKG", 7451000, "AS"],
"Hungary": ["HUN", 9768785, "EU"],
"Iceland": ["ISL", 353574, "EU"],
"India": ["IND", 1352617328, "AS"],
"Indonesia": ["IDN", 267663435, "AS"],
"Iran": ["IRN", 81800269, "AS"],
"Iraq": ["IRQ", 38433600, "AS"],
"Ireland": ["IRL", 4853506, "EU"],
"Isle of Man": ["IMN", 84077, "EU"],
"Israel": ["ISR", 8883800, "AS"],
"Italy": ["ITA", 60431283, "EU"],
"Jamaica": ["JAM", 2934855, "NA"],
"Japan": ["JPN", 126529100, "AS"],
"Jordan": ["JOR", 9956011, "AS"],
"Kazakhstan": ["KAZ", 18276499, "AS"],
"Kenya": ["KEN", 51393010, "AF"],
"Kiribati": ["KIR", 115847, "OC"],
"Korea, Dem. Rep.": ["PRK", 25549819, "AS"],
"Korea, South": ["KOR", 51635256, "AS"],
"Kosovo": ["XKX", 1845300, "EU"],
"Kuwait": ["KWT", 4137309, "AS"],
"Kyrgyzstan": ["KGZ", 6315800, "AS"],
"Laos": ["LAO", 7061507, "AS"],
"Latvia": ["LVA", 1926542, "EU"],
"Lebanon": ["LBN", 6848925, "AS"],
"Lesotho": ["LSO", 2108132, "AF"],
"Liberia": ["LBR", 4818977, "AF"],
"Libya": ["LBY", 6678567, "AF"],
"Liechtenstein": ["LIE", 37910, "EU"],
"Lithuania": ["LTU", 2789533, "EU"],
"Luxembourg": ["LUX", 607728, "EU"],
"Macao SAR, China": ["MAC", 631636, "AS"],
"Madagascar": ["MDG", 26262368, "AF"],
"Malawi": ["MWI", 18143315, "AF"],
"Malaysia": ["MYS", 31528585, "AS"],
"Maldives": ["MDV", 515696, "AS"],
"Mali": ["MLI", 19077690, "AF"],
"Malta": ["MLT", 483530, "EU"],
"Marshall Islands": ["MHL", 58413, "OC"],
"Mauritania": ["MRT", 4403319, "AF"],
"Mauritius": ["MUS", 1265303, "AF"],
"Mexico": ["MEX", 126190788, "NA"],
"Micronesia": ["FSM", 112640, "OC"],
"Moldova": ["MDA", 3545883, "EU"],
"Monaco": ["MCO", 38682, "EU"],
"Mongolia": ["MNG", 3170208, "AS"],
"Montenegro": ["MNE", 622345, "EU"],
"Morocco": ["MAR", 36029138, "AF"],
"Mozambique": ["MOZ", 29495962, "AF"],
"Burma": ["MMR", 53708395, "AS"],
"Namibia": ["NAM", 2448255, "AF"],
"Nauru": ["NRU", 12704, "OC"],
"Nepal": ["NPL", 28087871, "AS"],
"Netherlands": ["NLD", 17231017, "EU"],
"New Caledonia": ["NCL", 284060, "OC"],
"New Zealand": ["NZL", 4885500, "OC"],
"Nicaragua": ["NIC", 6465513, "NA"],
"Niger": ["NER", 22442948, "AF"],
"Nigeria": ["NGA", 195874740, "AF"],
"North Macedonia": ["MKD", 2082958, "EU"],
"Northern Mariana Islands": ["MNP", 56882, "OC"],
"Norway": ["NOR", 5314336, "EU"],
"Oman": ["OMN", 4829483, "AS"],
"Pakistan": ["PAK", 212215030, "AS"],
"Palau": ["PLW", 17907, "OC"],
"Panama": ["PAN", 4176873, "NA"],
"Papua New Guinea": ["PNG", 8606316, "OC"],
"Paraguay": ["PRY", 6956071, "SA"],
"Peru": ["PER", 31989256, "SA"],
"Philippines": ["PHL", 106651922, "AS"],
"Poland": ["POL", 37978548, "EU"],
"Portugal": ["PRT", 10281762, "EU"],
"Puerto Rico": ["PRI", 3195153, "NA"],
"Qatar": ["QAT", 2781677, "AS"],
"Romania": ["ROU", 19473936, "EU"],
"Russian Federation": ["RUS", 144478050, "EU"],
"Russia": ["RUS", 144478050, "EU"],
"Rwanda": ["RWA", 12301939, "AF"],
"Saint Vincent and the Grenadines": ["", 111000, "NA"],
"Saint Lucia": ["", 182000, "NA"],
"Samoa": ["WSM", 196130, "OC"],
"San Marino": ["SMR", 33785, "EU"],
"Sao Tome and Principe": ["STP", 211028, "AF"],
"Saudi Arabia": ["SAU", 33699947, "AS"],
"Senegal": ["SEN", 15854360, "AF"],
"Serbia": ["SRB", 6982084, "EU"],
"Seychelles": ["SYC", 96762, "AF"],
"Sierra Leone": ["SLE", 7650154, "AF"],
"Singapore": ["SGP", 5638676, "AS"],
"Sint Maarten (Dutch part)": ["SXM", 40654, "NA"],
"Slovakia": ["SVK", 5447011, "EU"],
"Slovenia": ["SVN", 2067372, "EU"],
"Solomon Islands": ["SLB", 652858, "OC"],
"Somalia": ["SOM", 15008154, "AF"],
"South Africa": ["ZAF", 57779622, "AF"],
"South Sudan": ["SSD", 10975920, "AF"],
"Spain": ["ESP", 46723749, "EU"],
"Sri Lanka": ["LKA", 21670000, "AS"],
"St. Kitts and Nevis": ["KNA", 52441, "NA"],
"St. Lucia": ["LCA", 181889, "NA"],
"St. Martin (French part)": ["MAF", 37264, "NA"],
"St. Vincent and the Grenadines": ["VCT", 110210, "NA"],
"Sudan": ["SDN", 41801533, "AF"],
"Suriname": ["SUR", 575991, "SA"],
"Sweden": ["SWE", 10183175, "EU"],
"Switzerland": ["CHE", 8516543, "EU"],
"Syria": ["SYR", 16906283, "AS"],
"Taiwan*": ["", 23574274, "AS"],
"Tajikistan": ["TJK", 9100837, "AS"],
"Tanzania": ["TZA", 56318348, "AF"],
"Thailand": ["THA", 69428524, "AS"],
"Timor-Leste": ["TLS", 1267972, "AS"],
"Togo": ["TGO", 7889094, "AF"],
"Tonga": ["TON", 103197, "OC"],
"Trinidad and Tobago": ["TTO", 1389858, "NA"],
"Tunisia": ["TUN", 11565204, "AF"],
"Turkey": ["TUR", 82319724, "AS"],
"Turkmenistan": ["TKM", 5850908, "AS"],
"Turks and Caicos Islands": ["TCA", 37665, "NA"],
"Tuvalu": ["TUV", 11508, "OC"],
"Uganda": ["UGA", 42723139, "AF"],
"Ukraine": ["UKR", 44622516, "EU"],
"United Arab Emirates": ["ARE", 9630959, "AS"],
"United Kingdom": ["GBR", 66488991, "EU"],
"United States": ["USA", 327167434, "NA"],
"US": ["USA", 327167434, "NA"],
"Uruguay": ["URY", 3449299, "SA"],
"Uzbekistan": ["UZB", 32955400, "AS"],
"Vanuatu": ["VUT", 292680, "OC"],
"Venezuela": ["VEN", 28870195, "SA"],
"Vietnam": ["VNM", 95540395, "AS"],
"Virgin Islands (U.S.)": ["VIR", 106977, "NA"],
"West Bank and Gaza": ["PSE", 4569087, "AS"],
"Yemen": ["YEM", 28498687, "AS"],
"Zambia": ["ZMB", 17351822, "AF"],
"Zimbabwe": ["ZWE", 1443901, "AF"]
}

continent = {
"NA": "[North America]",
"SA": "[South America]",
"EU": "[Europe]",
"AS": "[Asia]",
"OC": "[Oceania]",
"AF": "[Africa]"
}