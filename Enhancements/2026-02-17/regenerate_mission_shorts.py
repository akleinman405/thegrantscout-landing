#!/usr/bin/env python3
"""
Regenerate mission_short for all Template C emails from full mission_description.

V2: Proper ALL-CAPS -> sentence case conversion, better preamble stripping,
robust verb form handling, and smarter truncation.

The result must read naturally in:
    "I saw that {Org Name} {mission_short} and wanted to see if..."
So it must be a third-person present verb phrase like:
    "provides affordable housing for families"
"""

import psycopg2, csv, re, sys

from greeting_resolver import resolve_greeting, format_greeting_line

CSV_IN = "DATA_2026-02-17.3_generated_emails.csv"
CSV_OUT = "DATA_2026-02-17.3_generated_emails.csv"

# ── MANUAL OVERRIDES ──────────────────────────────────────────────────
# For missions where automated extraction fails or produces poor results.
# Key = EIN, Value = hand-written mission_short
MANUAL_OVERRIDES = {
    # From previous fix script (verified good)
    "222936068": "supports educational and religious programs",
    "825513595": "helps over 1,500 girls in India access education",
    "474784379": "supports women who have nowhere else to turn",
    "930717332": "provides care and supervision for children",
    "943111738": "improves health and well-being for clients",
    "200664128": "supports Walsh College programs and students",
    "571146474": "serves the community through live theater",
    "832331834": "helps families navigate financial challenges",
    "113623769": "supports student academic and career programs",
    "452440083": "promotes recirculating farm and agriculture practices",
    "844890857": "helps young people serve their country",
    "060919178": "supports senior socialization through programs and education",
    "844138362": "supports student success through community partnership",
    "010659307": "empowers the community through service and outreach",
    "201438278": "supports adolescent mothers and young fathers",
    "850411367": "supports local soil and water conservation districts",
    "842942167": "supports staff, parents, and community engagement",
    "472671013": "guides vulnerable populations of all ages",
    "593520130": "supports child abuse prevention and education",
    "383798900": "supports excellence in education and research",
    "860211414": "supports Cochise College students and programs",
    "330174451": "supports behavioral health services and programs",
    "362883552": "provides shelter and support for families in crisis",
    "112890302": "supports local economic development projects",
    "390961077": "promotes golf and community recreation programs",
    "260149521": "provides community outreach and support services",
    "943256879": "advances sports medicine education and research",
    "952535904": "advances laser technology education and safety",
    "364885536": "provides faith-based community services",
    "464085027": "serves community health programs",
    "942576101": "supports choral music performance and education",
    "060763897": "provides educational, cultural, and recreational programs",
    "760564888": "provides street lights and pest control services",
    "382647323": "develops future leaders in business and politics",
    "741191697": "provides educational, cultural, and social programs",
    "454474058": "provides free veterinary care for retired police dogs",
    "900901189": "promotes applied learning programs",
    "580619035": "provides care for surrendered and rescued pets",
    "113700175": "provides peer support and advocacy for parents",
    "461362294": "educates deaf and hard-of-hearing children",
    "742304542": "provides emergency shelter and crisis intervention services",
    "134038993": "operates an incubator for experimental performance",
    "043342182": "promotes racial justice and community health",
    "463134601": "strengthens community resilience before and after disasters",
    "270513560": "promotes positive youth development and family support",
    "954840800": "promotes personal development and organizational leadership",
    "251894523": "supports resilient solutions for watershed health",
    "204570887": "educates students with learning differences",
    "113247651": "provides a transformative musical education for students",
    "310736673": "creates community excellence through arts and culture",
    "742428647": "provides recreational softball for girls",
    "043341661": "inspires and enables all young people to reach their potential",
    "264106369": "inspires high school students to engage civically",
    "203890194": "educates and empowers members of the Pontiac community",
    "208540050": "supports American Muslim storytelling and representation",
    "860947944": "provides free long-term care for sick children",
    "203496878": "inspires curiosity and creativity in children",
    "452721646": "educates and inspires children holistically",
    "626074113": "promotes regional arts and cultural events",
    "272081900": "educates and empowers veterans to live engaged lives",
    "850626336": "promotes decent, safe, and sanitary housing",
    "830317641": "supports and expands access to quality health services",
    "475449750": "supports community development throughout rural North Dakota",
    "822026061": "improves healthcare through innovation and biomedical research",
    "263042342": "provides a space where teens can explore and grow",
    "237001357": "educates and enriches lives through orchestral music",
    "232798276": "supports employer recruitment and economic growth in the Lehigh Valley",
    "043769200": "helps students grow spiritually and intellectually",
    # Additional overrides for known problem cases
    "825228511": "helps students become collaborative problem-solvers",
    "830766028": "provides programs and services for people with disabilities",
    "581946962": "promotes the Gwinnett County community through charitable giving",
    "472058404": "serves young adults with physical and intellectual disabilities",
    "202737719": "promotes organ and tissue donation for transplantation and research",
    "161005743": "educates students through hands-on student government experience",
    "231599650": "provides facilities and services to support special education programs",
    # Round 2: Remaining 159 issues (preamble/caps/org-name/IRS language)
    "010358141": "works with the community to end domestic violence in York County",
    "043273300": "promotes safety, healing, and justice for child victims of abuse",
    "043673627": "provides a diverse, cooperative Montessori learning community for children",
    "043726675": "provides transformational housing and support for women rebuilding their lives",
    "050377538": "works toward a future free of domestic violence",
    "050512037": "provides quality support, training, and programming for children with autism",
    "131984011": "provides financial professionals with networking and educational opportunities",
    "132729071": "advocates for and supports behavioral health member agencies",
    "134204733": "provides industry professionals with quality resources and networking events",
    "134242224": "promotes youth soccer and recreation for children in McHenry County",
    "200022399": "supports communities in West Virginia pursuing self-directed development",
    "200835490": "provides ancillary instruction and learning experiences for youth",
    "202534366": "preserves and develops Korean cultural heritage in the United States",
    "202573758": "helps vulnerable Californians navigate housing and consumer finance issues",
    "202607873": "provides a German immersion education for students",
    "203193765": "enriches the lives of young people through learning and creating theater",
    "204225394": "cultivates appreciation of Black drama arts and accessible theater",
    "204251986": "provides childcare, private school, and summer programs for families",
    "205296438": "creates hope and opportunity for children with autism and their families",
    "205666260": "creates an inclusive community of people with purposeful and independent lives",
    "210634563": "strengthens individuals and families by empowering people to care for themselves",
    "222547057": "helps children become good friends and proficient problem-solvers",
    "223262213": "provides leadership in planning early intervention services in New Jersey",
    "232041622": "provides counseling, foster care, and services for young people and families",
    "233001411": "promotes inclusive economic growth through immigrant integration",
    "237067376": "advocates on behalf of independent education in Hawaii",
    "237094560": "serves the mentally and physically disabled through ministry and outreach",
    "237102928": "supports youth programs and community service through charitable giving",
    "237348710": "improves quality of life for people and pets through animal shelter services",
    "251271659": "enriches lives through innovative art exhibitions and programs",
    "251625390": "provides religious, charitable, and educational services for the Catholic community",
    "251738322": "raises and manages funds to support services and programs for children",
    "261364376": "creates environments where individuals are valued and encouraged to grow",
    "262700504": "improves health and well-being through education and access to dental care",
    "270950140": "monitors and promotes the health of marriage and family life",
    "271530938": "provides automated external defibrillators and CPR training in schools",
    "272191898": "provides quality, affordable mental health care in the San Fernando Valley",
    "272194956": "advances education reform in public and charter schools",
    "274295514": "provides seeds of opportunity for people to make a sustainable difference",
    "311011321": "encourages philanthropic support of Marietta Memorial Hospital and related services",
    "320003071": "provides a home for culture, ideas, and belonging on the east side of Los Angeles",
    "331037577": "enhances the region's economic vitality through tourism marketing and events",
    "340845030": "educates and inspires people to appreciate the natural world",
    "341262368": "promotes artistically and culturally significant film through education",
    "341996138": "produces vibrant theater created by emerging and accomplished artists",
    "351854805": "enhances teaching and learning at private colleges in Indiana",
    "352372805": "provides tribal citizens with access to affordable capital for business loans",
    "362937848": "leads community efforts to eliminate child abuse through treatment and education",
    "363037232": "builds regional relationships and secures resources for college students",
    "363323142": "provides hope and support to individuals affected by head and neck cancer",
    "363689665": "creates and provides services that help South Asian immigrants adjust and thrive",
    "364200490": "inspires, educates, and provokes exploration through innovative conservatory programs",
    "364672694": "motivates, educates, and trains individuals to become leaders",
    "366109822": "offers a platform for bold artistic experimentation",
    "366154098": "connects the public with the work and ideas of living artists",
    "371340071": "preserves and enhances natural resources by supporting ecological education",
    "382236821": "empowers neighbors in low-income communities through basic needs assistance",
    "382391442": "revitalizes neighborhoods and promotes community investment",
    "391225229": "nurtures open-minded individuals who embrace the world with compassion",
    "391657328": "administers and implements job training programs in southern Wisconsin",
    "411429410": "promotes law teaching and research through computer-assisted education",
    "411466054": "fosters an ethic of stewardship for farmland, communities, and natural resources",
    "412117257": "serves as an American Indian community development resource",
    "426080176": "serves the community with programs for men, women, and children of all ages",
    "431094348": "enhances the cultural life of Kansas City through professional contemporary theater",
    "452661390": "raises money to support research, education, and diversity in archival work",
    "452947613": "improves the health of women, children, and families in Sierra Leone",
    "460779614": "assists low-income students, including female soccer players, through education",
    "461577827": "provides assistance for the health and welfare of at-risk children and families",
    "462159711": "helps ensure every child has the foundation to learn and grow",
    "463159251": "works to eradicate homelessness for LGBTQ+ youth ages 18-24",
    "463275286": "promotes clean energy and environmentally friendly solutions",
    "463277220": "reaches the next generation through the arts and personal development programs",
    "463701580": "supports religious, charitable, and educational community programs worldwide",
    "464265280": "bridges the technology gap for LGBTQ individuals",
    "464578553": "restores and supports Native American food systems through education and advocacy",
    "464868482": "educates the public about population and environmental sustainability",
    "464952693": "serves as the statewide professional association for community health workers in Oregon",
    "470731254": "develops impactful philanthropic projects to enrich the Omaha community",
    "472208322": "helps engage the community in specialized healthcare and patient care programs",
    "472443093": "helps youth and families lead healthy and productive lives",
    "473046049": "collaborates with parents and nonprofits to create culturally relevant programs",
    "474275163": "provides homeless women with supportive resources and a caring community",
    "475074106": "provides volleyball training opportunities for boys and girls ages 5 to 18",
    "476000332": "supports the preservation and appreciation of Nebraska history",
    "510161757": "supports students and programs at a community college in Mississippi",
    "520881396": "provides information services and resources for university education programs",
    "521962712": "supports vibrant small business communities through mentoring and education",
    "521986104": "supports the National Cryptologic Museum and public education about cryptology",
    "522100915": "helps develop students' capacity and character for lifelong purpose",
    "522303612": "provides training and technical support for health and human service providers",
    "540605800": "provides a home for abused and neglected children",
    "540884554": "creates a nurturing environment for students with particular academic needs",
    "541030634": "fosters appreciation and understanding of animal conservation",
    "541427910": "serves the community through religious, educational, and charitable programs",
    "541495814": "provides child care services for families in the community",
    "541824385": "improves the quality of life for individuals with autism and their families",
    "546045072": "creates a vibrant artistic space for the community to engage in theater",
    "550810542": "operates a rural health network promoting public health in New York",
    "550856553": "provides birthday parties to children living in homeless shelters",
    "556000958": "serves local communities through orchestral programs that educate and entertain",
    "571233653": "promotes environmental, cultural, and educational events for the community",
    "581640904": "provides shelter, counseling, and advocacy for families in crisis",
    "582075193": "bridges the financial and emotional gaps faced by organ transplant recipients",
    "582204209": "creates a quality of life that supports the development of families",
    "586074088": "provides animal welfare services including adoption and rescue programs",
    "590830750": "provides a healthy environment for neglected boys",
    "610458359": "empowers children, youth, and families to reach their full potential",
    "610929390": "works to improve child well-being and policies that affect young people in Kentucky",
    "650307858": "enriches lives through inspiring musical experiences",
    "650832961": "provides faith-based assistance and support to neighbors in need",
    "650846695": "brings orchestral music of the highest caliber to South Florida",
    "650848128": "serves Miami-Dade County residents with community support programs",
    "650874830": "assists families, adults, seniors, and children with food and services",
    "710818518": "provides international educational and cultural exchange experiences",
    "742239886": "provides funding to improve the health of Texans through charitable programs",
    "742550748": "provides support systems for individuals and families affected by HIV/AIDS",
    "742729189": "serves as a no-kill animal shelter for abandoned and injured animals",
    "742805791": "improves economic development in northern New Mexico",
    "743091110": "offers brilliant musical performances and in-person experiences",
    "752717782": "supports the health of families receiving health care in the community",
    "756085616": "provides care and education for children in need",
    "760367244": "provides shelter for people with physical and mental health challenges",
    "810615231": "develops and sustains a tradition of soccer excellence for youth",
    "812871377": "provides financial assistance and care coordination for the LGBTQIA+ community",
    "813840811": "provides opportunities for people 50+ to thrive through community activities",
    "813872831": "brings world-celebrated ballet companies and dancers to the Sun Valley area",
    "815449140": "inspires young people to pursue careers in accounting",
    "816014910": "provides shelter for unwanted and stray animals in the community",
    "821193065": "provides an innovative educational experience rooted in financial literacy",
    "821304950": "provides high-quality psychotherapy for patients with limited resources",
    "821577991": "empowers youth facing adversity through long-term mentoring",
    "825467031": "promotes the economic development of Hispanic-owned businesses",
    "833710153": "provides a loving, safe, and supportive educational environment for students",
    "841069931": "provides quality childcare in a learning environment for young children",
    "841149609": "connects a diverse community through inspiring arts experiences",
    "841172799": "fosters communication and collaboration among academic computing institutions",
    "843484606": "fosters growth in local startup activity by supporting entrepreneurs",
    "851934638": "promotes research at the University of Massachusetts Lowell",
    "852482031": "empowers college students through comprehensive basic needs support",
    "853156907": "advances the common good through literacy and community engagement",
    "853282219": "provides excellent choral and music education for young singers in grades K-12",
    "873479318": "operates a charter school ensuring academic success for students in grades K-5",
    "873701368": "operates a K-12 charter school focused on science education",
    "881149236": "empowers student-athletes through opportunities to leverage their influence",
    "881453619": "forms schools that develop students through classical education",
    "882226986": "serves and empowers a national alliance of state school boards associations",
    "884067747": "supports online content creators who share their work with integrity",
    "900641325": "equips students for success through the power of reading",
    "901009621": "works to reduce poverty and food insecurity through employment training",
    "920068910": "works to reduce the suffering of dogs and cats in Alaska",
    "920141715": "offers support, shelter, sustenance, and skills to those in need",
    "930333036": "serves the community by providing family-friendly programs and events",
    "931179323": "links neighborhoods with convenient and attractive transportation",
    "942428993": "provides dynamic and inclusive performing and visual arts education",
    "943067129": "provides temporary housing for homeless individuals and families",
    "943113745": "explores the Jewish experience in Oregon and teaches Holocaust education",
    "946064356": "makes live musical experiences accessible to everyone",
    "953038398": "cultivates the vitality of Long Beach neighborhoods through the arts",
    "990187576": "enriches individuals and communities through performing arts education",
    "990351832": "enhances the region's economic vitality and quality of life through tourism",

    # Orgs whose missions are too corporate/technical/vague for the template
    "454079029": "develops open data standards for the real estate industry",
    "752426687": "ensures quality standards in athletic training education",
    "640179401": "promotes thrift and financial well-being for its members",
    "311705913": "provides high-quality child care programs",
    "300075905": "provides professional development for nonprofit leaders",
    "351382793": "supports parents, families, and service providers for people with disabilities",
    "650530384": "supports Florida's 28 community colleges and their students",
    "381539997": "supports Michigan 4-H youth development programs",
    "431304714": "supports programs that promote quality of life for senior residents",
    "521720580": "supports long-term care programs for seniors in New Jersey",
    "942914703": "helps young children with hearing loss reach their communication potential",
    "822548805": "helps educators design meaningful educational experiences",
    "830333159": "provides inspiring western adventure programs in Jackson Hole",
    "942684774": "promotes the health, dignity, and rights of older adults",
    "261753089": "brings hope and opportunity to families in extreme poverty in Africa",
    "530214281": "promotes the welfare and rehabilitation of blinded veterans",
    "731116755": "supports community health, education, and economic development",
    "591743694": "fosters professional and scholarly activities in criminal justice",
    "237399484": "improves clinician competence in cervical disease prevention",
    "363636933": "supports people affected by cancer through wellness programs",
    "650016849": "provides youth sports programs for children in the community",
    "841403727": "promotes healthy environments and communities through ministry",
    "463432541": "provides community radio programming for Martha's Vineyard",
    "261240327": "empowers a caring community that supports the well-being of every child",
    "486149549": "provides an early learning environment that nurtures children's growth",
    "133861648": "serves students and alumni from underrepresented communities",
    "300437443": "supports adults with mental illness through employment and community access",
    "391133513": "promotes contemporary art through exhibitions and education",
    "561839309": "provides adoption services, foster care, and family support",
    "263631295": "supports philanthropic programs that benefit senior communities",
    "562501124": "serves the local community through Christian child care programs",
    "462536926": "provides a child-centered Montessori education for grades K-7",
    "475518844": "helps veterans navigate the VA claims process",
    "136400777": "provides enriching summer camp experiences for children",
    "060850379": "provides children facing adversity with strong mentoring relationships",
    "464064528": "serves the community through outstanding musical theater",
    "550727658": "creates better employment opportunities through technology and innovation",
    "381969044": "ensures quality educational experiences for medical residents",
    "752638117": "inspires and engages communities through theater",
    "822604098": "provides long-term mentoring for children facing adversity",
    "311561944": "provides empowerment through adaptive sports and education",
    "560755213": "promotes the unique cultural offerings of the Wilmington community",
    "384105767": "improves educational and life outcomes for Black students in Oakland",
    "260833850": "helps residents break cycles of poverty in New Orleans",
    "862256098": "promotes the health and well-being of underserved communities",
    "810592109": "provides programs that strengthen families and communities",
    "853300505": "advances racial equity through theater",
    "223679194": "supports court-appointed advocates for abused and neglected children in New Jersey",
    "464996721": "fosters collaboration in shared mobility and sustainable transportation",
    "464390683": "promotes public understanding of science and technology",
    "263725345": "serves as a crisis center connecting people to community resources",
    "951661090": "provides compassionate shelter and care for animals in need",
    "853477757": "trains and places workers in residential construction trades",
    "454394892": "inspires children to love learning through hands-on education",
    "200379279": "provides affordable housing and support services for low-income residents",
    "061053241": "teaches children the fundamentals and values of hockey",
    "232846336": "enriches lives and connects people through the arts",
    "363374370": "provides shelter, hope, and dignity for those experiencing homelessness",
    "421242565": "provides programs and research for students and educators",
    "880301113": "increases opportunities for children with disabilities and their families",
    "146032117": "provides services for students, community, and alumni of Ulster County",
    "550420373": "supports programs for girls in grades K-12",
    "770498274": "provides Christian medical care in underserved regions worldwide",
    "561995085": "operates a public charter school focused on primary education",
    "452852041": "supports public freedom and open exchange on the internet",
    "383114474": "advocates for people with disabilities and barrier-free communities",
    "141789139": "serves as a cornerstone of the community through lifelong learning",
    "586001278": "provides a creative residency program for artists and scientists",
    "911852210": "provides transportation for elderly and disabled residents",
    "264425295": "provides quality education in an Islamic learning environment",
    "942344976": "helps people with disabilities become more independent",
    "471683881": "prepares young people for career success in New York",
    "521759646": "empowers women through character development and professional training",
    "880468000": "promotes responsible gaming and industry best practices",
    "710876701": "promotes community access and independence for people with disabilities",
    "930727839": "provides ongoing support for Salem-area Catholic schools",
    "462211150": "provides youth soccer development for players in Skagit County",
    "382725232": "provides literacy support tailored to adult learners",
    "421461422": "inspires children to imagine and discover through the power of play",
    "100007967": "provides academic support, mentoring, and leadership for youth",
    "510220694": "inspires growth in all children by engaging families in learning",
    "521720876": "inspires low-income and first-generation youth to achieve college success",
    "410712101": "brings the agricultural community together through county fair programs",
    "452378417": "provides a learning environment that extends beyond the classroom",
    "020491761": "provides quality performing arts instruction for young people",
    "363913497": "protects and stewards land and water resources",
    "916073780": "supports educational opportunities and student success at Tacoma Community College",
    "770435044": "provides youth soccer development and amateur athletic competition",
    "382807457": "provides permanent supportive housing for people experiencing homelessness",
    "851088834": "supports Indigenous language revitalization and cultural preservation",
    "232745763": "improves child well-being by supporting involved fatherhood",
    "466017026": "inspires the best in everyone through music",
    "826003780": "operates a volunteer-driven community food pantry",
    "843634157": "fosters healthy development in children of all abilities",
    "481093604": "helps high school graduates access higher education",
    "822004573": "empowers and educates communities on mental health and wellness",
    "451043395": "provides therapeutic equestrian programs for people with disabilities",
    "352135367": "provides a nurturing educational environment for young children",
    "030447156": "provides students with personalized and flexible online education",
    "522254430": "provides training in citizen leadership and human rights",
    "010427824": "provides ceramic arts education through residency and retreat programs",
    "843519874": "provides support and a place for continued healing after hospitalization",
    "381790921": "inspires and empowers a diverse population of students",
    "943297241": "provides affordable spay and neuter services for community cats",
    "930408077": "promotes mountaineering and wilderness exploration",
    "841175450": "supports college students and programs meeting industry demands",
    "473485977": "provides organizational guidance and consulting for religious organizations",
    "840834567": "supports the advancement of Pueblo Community College students",
    "116027312": "helps communities plan for land use and environmental protection",
    "841831744": "provides compassionate adoption services for families",
    "521918702": "provides housing, job training, and counseling services in DC",
    "463280693": "helps veterans with lodging, food, and transportation services",
    "465563874": "provides children with an outstanding academic foundation",
    "201535497": "provides early intervention listening and spoken language services",
    "756061186": "supports excellence and impact in the arts",
    "461127723": "provides young students a fun and fair flag football experience",
    "870575845": "supports medical and dental treatment for children in need",
    "541902943": "provides high-quality psychiatric and residential care for children",
    "223126832": "provides an inclusive, enriching learning environment for young children",
    "760621817": "promotes education about the craft arts and their history",
    "841383214": "provides therapeutic recreation for people with disabilities",
    "721223347": "provides affordable housing, business training, and youth programs",
    "844595782": "creates indigenous agriculture and food systems for tribal communities",
    "351710780": "provides literacy instruction and referral services",
    "223230201": "provides quality programming for adults with autism",
    "942842712": "provides a well-rounded public education for all students",
    "840738408": "enriches the cultural, social, and educational life of the community",
    "731470933": "provides religious education and reference materials",
    "141275432": "inspires wonder about science and technology",
    "541241771": "provides a safe haven for survivors of domestic violence",
    "550487705": "provides educational, social, and recreational programs for seniors",
    "251635184": "provides entertaining and educational programming for children",
    "610916756": "provides comprehensive services to survivors of sexual violence",
    "351389305": "supports prison chaplains and encourages incarcerated individuals",
    "221660518": "promotes the health, social, and educational development of youth",
    "942372185": "helps artists sustain their creative work over time",
    "134158264": "fosters global citizens who contribute to international well-being",
    "911178405": "provides crisis services, support, and advocacy to crime victims",
    "472253259": "preserves the history of the videogame industry",
    "030364018": "provides health and recreation programs for area residents of all ages",
    "843811937": "provides meals and hygiene items to children in need",
    "860909286": "promotes academic and life skills development for students",
    "383685603": "serves the people of Palestine through community programs",
    "951775142": "provides educational programs for youth in diverse subjects",
    "900168625": "inspires a love of learning in science and technology",
    "330547453": "empowers an enhanced quality of life for people with disabilities",
    "364686736": "provides educational and cultural opportunities for the general public",
    "392021628": "provides a high-quality early learning experience for children",
    "592203965": "improves quality of life and economic opportunities in the community",
    "953695686": "provides high-quality education for the whole child",
    "381867280": "provides vocational, personal, and social development opportunities",
    "716058254": "educates students on economics, personal finance, and free enterprise",
    "042695256": "supports local health departments in meeting community needs",
    "341769835": "creates an enduring appreciation of music in the community",
    "731570162": "promotes community engagement through faith-based outreach",
    "900131857": "provides a supportive educational environment for children",
    "416057985": "fosters improved patient care through education and research",
    "170785041": "promotes the culture and heritage of indigenous peoples",
    "232775806": "advocates for and empowers prenatal and parenting families",
    "680070136": "provides quality child care in Marin County, California",
    "521784596": "promotes the success of VA-affiliated nonprofit research organizations",
    "231498877": "promotes women's leadership for meaningful community impact",
    "222658964": "protects vital lands and waters throughout Midcoast Maine",
    "980166250": "provides therapeutic horsemanship programs for people with challenges",
    "760318872": "empowers students to stay in school and succeed",
    "200110711": "provides programs and services to benefit children and families",
    "912093451": "provides the academic and emotional support students need to succeed",
    "650257588": "provides childcare, early education, and social services for families",
    "943240968": "promotes the love of soccer and youth development",
    "542025186": "supports teaching and learning inside Richmond public schools",
    "631143875": "provides a multi-purpose cultural facility for the community",
    "454079423": "provides vibrant arts and culture programming",
    "042152010": "provides thought-provoking learning experiences connecting past and present",
    "820372006": "provides emergency shelter and crisis services for domestic violence survivors",
    "203029784": "helps children develop critical life skills through the arts",
    "201344722": "supports Shepherds Ministries through communication and philanthropy",
    "263660127": "empowers women entrepreneurs by providing access to capital and mentoring",
    "103397750": "preserves and interprets the cultural heritage of the region",
    "621043294": "provides healing for children, adults, and families affected by sexual assault",
    "874389463": "delivers accessible, patient-centered healthcare with quality and compassion",
    "202136431": "provides food and health assistance to individuals in the local community",
    "562500062": "supports and challenges each child to develop critical thinking skills",
    "731284538": "prevents child abuse by providing evidence-based parent education",
    "334148044": "provides affordable housing and supportive services in the community",
    "351781229": "provides housing for homeless families while assisting them to self-sufficiency",
    "591298067": "provides quality residential and outpatient substance abuse treatment",
    "990241019": "provides a Christ-centered, biblically based education",
    "560599234": "provides a safe living environment for abused and neglected children",
    "824029826": "provides equine-assisted therapy and community horseback riding",
    "030179595": "develops responsible and productive children and families",
    "237066181": "provides a forum for professional scientific communication in diving medicine",
    "843111107": "protects and restores salmon populations and aquatic habitats",
    "451028375": "enriches the lives of preschool-age children and their families",
    "272083749": "provides housing and assistance for women and children in need",
    "311345575": "provides affordable housing for individuals with developmental disabilities",
    "222461852": "provides educational instruction for children in preschool through sixth grade",
    "026011969": "protects and enhances the special environment of the Lake Sunapee region",
    "131707897": "promotes understanding and education about the Holocaust",
    # Round 3: Verb agreement, broken preambles, org name, truncation, proper nouns
    # Broken preambles / formatting
    "952281908": "provides physical, emotional, and spiritual support to children and families",
    "263381206": "meets the physical, emotional, and spiritual needs of the community",
    "953146855": "provides quality child care and child development services",
    "391889441": "helps all students reach their potential, both academically and morally",
    "561421977": "provides additional funding for innovative programs that advance student achievement",
    "411386089": "empowers individuals and communities by helping people buy, fix, and keep their homes",
    "411570750": "inspires the next generation of innovators, engineers, and creative problem-solvers",
    "465068934": "provides professional outpatient mental and behavioral health counseling",
    "510239450": "improves health through the development of primary care research",
    "593685521": "serves as the united voice for excellence in public education",
    "030472883": "provides court-appointed volunteer advocates for abused and neglected children in DC",
    "141786202": "establishes a unified voice for children and youth with challenges",
    "821110902": "raises awareness and provides aid to disabled U.S. military veterans",
    "841587575": "advocates for and supports the health of the community through partnerships",
    "141798918": "supports programs and activities to improve the community of Hunter, New York",
    "815453995": "advances community health care services regardless of ability to pay",
    # Verb agreement: ambiguous words not caught by automated fix
    "753057770": "grows and supports a vibrant arts center with engaging opportunities",
    "463211483": "serves and supports developmentally disabled individuals",
    "650363222": "develops and supports a local system of care for mothers and families",
    "464930592": "advances literacy and helps close the achievement gap for students",
    "834126446": "protects and preserves the Gamble House in perpetuity",
    # Verb agreement: multi-verb lists needing manual conjugation
    "420680248": "excites, engages, and educates the community through the arts",
    "582449646": "educates, empowers, and inspires children and teens living with diabetes",
    "201909377": "engages, inspires, and educates students for an options-rich future",
    "742036976": "preserves, develops, and promotes the arts and culture of Chicano and Latino peoples",
    "043406670": "preserves and interprets cultural and natural heritage resources",
    "350989082": "shelters, rescues, and protects animals from abuse and mistreatment",
    "951880698": "collects, preserves, and promotes the culture and history of Santa Catalina Island",
    "361930035": "conserves, restores, and promotes the sustainable use of natural resources",
    "460949763": "supports scientific research, public safety, and education about Atlantic white sharks",
    "814126222": "researches, partners, and advocates for projects that promote healthier communities",
    "752367391": "provides child day care and Head Start classes for low-income families",
    "200031464": "manages scholarships for qualified graduates of Alexandria public schools",
    # Org name repeated redundantly in text
    "850534394": "advances printed circuit engineering through education and professional development",
    "953849600": "raises funds for rehabilitation programs serving patients with spinal cord injuries",
    "136141078": "promotes leadership development and scholarships for fraternity members",
    "460475333": "promotes research into the causes of myeloma, bone cancer, and related diseases",
    "222126370": "provides culturally relevant social services and advocacy for the community",
    "232034407": "supports educational programs of the U.S. Army War College",
    "371501970": "promotes the teaching, learning, and performance of chamber music",
    "270314493": "supports and promotes arts organizations in Nevada County",
    # Complex: preamble + state + org name
    "471158982": "cultivates a thriving arts community in Central Florida",
    "591000186": "provides educational opportunities for youth through local county programs and camps",
    "203415545": "provides Spanish language information and referral services to the community",
    "451447370": "provides medical, health, educational, and transportation services in Northern Kentucky",
    "825141973": "empowers youth facing obstacles through long-term mentoring relationships",
    "465499118": "provides a trilingual education for students",
    "251773112": "provides job training and vocational assistance to people with disabilities",
    "830217245": "enriches the lives, well-being, and independence of seniors in Riverton",
    "541067694": "provides safe, affordable housing for low-income seniors",
    # Truncation at comma (reads badly before "and wanted to see")
    "391484989": "provides excellent health care, housing, and community-based services",
    "272012662": "develops projects and programs that promote community economic development",
    "820385213": "empowers individuals affected by domestic violence and sexual assault",
    "391783748": "helps health care consumers navigate a complex health care financing system",
    "853336715": "advances workforce development in STEM fields",
    "331173163": "supports sustainable equine welfare programs around the world",
    "237013531": "promotes social, recreational, cultural, and educational programs for seniors",
    "570703785": "operates community centers providing programs and activities for seniors",
    "570742866": "provides alcohol and drug abuse treatment and prevention services",
    "042472369": "provides opportunities for children to grow socially and emotionally",
    "222778232": "collects, conserves, and documents Armenian cultural heritage",
    "383849052": "promotes inclusivity and equal accessibility in academic and social settings",
    "550479715": "provides vision, education, training, and resources to rescue missions",
    "850474099": "provides compassionate and safe grief support for children",
    "823547898": "provides technical construction skills and job readiness training",
    "800912572": "strengthens the voice for clean energy through education and outreach",
    # Proper noun capitalization
    "042104343": "provides information and support to the Jewish community",
    "201949540": "enhances the University of North Carolina at Wilmington's educational mission",
    "452600372": "operates a public charter school in Lee County, Florida",
    # Round 4: Final verb agreement + truncation fixes
    "831431959": "establishes and sustains a unique cyber ecosystem for education",
    "813587723": "researches and provides interventions to meet the needs of each child",
    "362181657": "develops and supports cold chain systems and networks",
    "854160029": "establishes and operates a charter school for a diverse community",
    "420772544": "fosters the enjoyment of and support for the arts",
    "010211486": "develops community, character, and personal growth through YMCA programs",
    "742542664": "builds early literacy in children and families through healthcare and education",
    "262969004": "provides high quality and affordable educational courses and travel programs",
    "043266422": "improves global health by advancing angiogenesis-based medicine and diet",
    "420761060": "connects people and resources to advance community health and education",
    "521155779": "promotes peace by furthering mutual understanding and friendship",
    "770384453": "empowers people with disabilities to grow creatively and professionally",
    "841169001": "provides educational and charitable funding for students and faculty",
    "882523319": "supports emerging musicians with grants and collaborative opportunities",
    "300098388": "provides and promotes exceptional standards of education and networking",
    # Round 5: Issues found in random sample verification
    "753091931": "assists parents in the formation of their children through classical Catholic education",
    "650009277": "improves access to quality health care and provides preventive health education",
    "271010441": "develops and sustains a thriving local economy through job attraction and investment",
    "591479653": "partners with Christian parents to develop students with hearts prepared to serve",
    "351148133": "provides a high quality, safe, and stimulating educational foundation for children",
    "830695359": "fosters collaborations that build safe and respectful learning communities",
    "020651198": "provides effective solutions to improve the lives of foster children",
    "582139259": "unites the community to support and empower families and prepare children to succeed",
    "942701342": "practices and teaches an optimal approach to education and care of young children",
    # Round 6: Broader scan issues (org name in text, preambles, truncation)
    "222235002": "provides people of all ages and cultures with creative arts experiences",
    "593193026": "provides athletic and dance opportunities for children",
    "990089250": "ensures compassionate, informed care of all animals on Kauai",
    "581449533": "provides quality learning in a nurturing cooperative preschool environment",
    "471804087": "provides an affordable legal education through online learning",
    "263765706": "trains the church to build student-led teams that serve their communities",
    "134186589": "develops health care programs for underserved communities",
    "050439495": "empowers people with disabilities to live independently in the community",
    "473700373": "develops affordable housing for low-income families",
    "231365188": "provides residential care and education for at-risk children and youth",
    "760679202": "provides quality Christian education and strives for excellence",
    "941526940": "supports student programs and activities at the university",
    "310791031": "preserves and presents the history and culture of Chillicothe",
    "260035224": "supports the conservation of endangered wildlife in central Africa",
    "550751563": "instills hope and self-sufficiency through gifts-in-kind programs",
    "221501370": "serves as a community-based resource for women in Hudson County",
    "823990062": "provides access to credit and financial resources for underserved communities",
    "610719760": "assists developmentally and intellectually disabled adults",
    "391674150": "connects manufacturers' surplus goods with nonprofits serving those in need",
    "470897469": "provides tuition-free education for students who need flexible learning options",
    "521910387": "provides affordable housing preservation for low-income residents",
    "264653381": "changes the lives of abused and neglected children through court-appointed advocates",
    "043241307": "inspires underrepresented students to pursue careers in biomedical science",
    "651275162": "provides life-saving medicines at low cost to underserved patients",
    "141918174": "provides strength-based quality support to families",
    "464447642": "supports the launch and growth of high-quality public charter schools",
    "820360653": "provides a Montessori-inspired education for young children",
    "454817136": "supports medical missions and healthcare programs in developing countries",
    "237447371": "preserves and shares a historic Gilded Age home with the public",
    "746000772": "sponsors and presents musical performances and educational programs",
    "061570097": "provides tennis and educational programs for underserved youth",
    "911842787": "supports the resident camping program for youth",
    "954871106": "empowers residents to build stronger communities",
    "542006078": "provides affordable housing for people with developmental disabilities",
    # Over-stripped by trailing adjective cleanup
    "521639499": "promotes the development of children from infancy through kindergarten",
    "041988955": "enriches the community by stewarding Mechanics Hall as a world-class performance venue",
    "222817982": "preserves and operates Morven Museum and Garden as a public landmark",
    "480849346": "provides educational and technical information to public water systems in Kansas",
    # Round 7: Fix remaining preambles, comma-and, trailing, org-in-text, short issues
    # -- a-nonprofit preambles --
    "362193600": "ensures quality early childhood education and parent support services for families",
    "112973066": "provides education and therapy services for children with special needs",
    # -- bare infinitive --
    "521182326": "presents programs that promote community and a love of the arts in Washington, D.C.",
    # -- comma-and ambiguity fixes --
    "204638961": "provides young hockey players the opportunity to develop their talents",
    "811991919": "produces and disseminates educational programming through media technology",
    "941196194": "supports youth development through educational and philanthropic programs",
    "262477706": "cultivates community markets that utilize local resources",
    "760442428": "promotes Chinese language and cultural education",
    "311537194": "provides quality experiences that enrich and educate the community",
    "340947516": "proclaims God's love through community service",
    # -- mission preambles --
    "451601843": "makes learning music accessible and equitable",
    "200764068": "provides training and financial support to missionary aviators",
    "261388409": "empowers children and adults with Tourette Syndrome through education and advocacy",
    "210613118": "provides a rigorous academic program from a Christian worldview",
    "592596359": "improves the lives of young people through education and employment",
    "232485020": "improves the health and well-being of individuals living with HIV/AIDS",
    "010211798": "improves the health and safety of Mount Desert Island residents",
    "475454938": "helps young adults create a pathway to independence through food service training",
    "770076649": "builds homes and community in Fresno County",
    "264449380": "serves neighbors in poverty with Christian compassion",
    "363411361": "raises endowment funds to support care services for seniors",
    "760695721": "promotes Vedic heritage and spreads Vedic knowledge to future generations",
    "521773753": "strengthens health systems through locally driven partnerships",
    "863298938": "meets Black men where they are with vital social programs",
    "251457559": "assists individuals with disabilities to become independent and productive",
    "205217230": "provides a safe environment for youth soccer instruction and competition",
    "770464784": "promotes awareness of the Monterey Bay ecosystem through educational field trips",
    "450443517": "inspires the discovery of science through hands-on experiences",
    "752185073": "helps establish basic skills through joyful teaching methods",
    "455307975": "provides support and resources for people recovering from addiction",
    "741359405": "assists individuals with disabilities through rehabilitation services",
    "911184237": "provides alcohol and drug treatment counseling and education",
    "843606525": "helps underserved youth develop skills for education and career success",
    "042476258": "empowers immigrants through education, guidance, and support services",
    "132556242": "provides a camp for children with cancer",
    "204154215": "provides a well-rounded liberal arts education for students",
    # -- org-in-text --
    # 237447371 and 510161757 and 043406670 fixed above
    # -- short entries --
    "841314292": "fosters academic and emotional growth for children in metro Denver",
    "954838321": "provides educational and relief services in underserved countries",
    # -- the/our/its/we preambles --
    "742933669": "works with children and families to provide a healthy family environment",
    "310537139": "creates an organized center of thought and action among women",
    "270615591": "provides compassionate support to those affected by sexual trauma",
    "010633672": "brings the community together to support young children in Larimer County",
    "382699957": "brings peaceful resolution to conflicts through mediation and training",
    "263438302": "helps families in Potrero Hill, Dogpatch, and Mission Bay thrive",
    "841187080": "provides Torah education to students from kindergarten through high school",
    "421252893": "walks with those who have fallen on hard times to help them find hope",
    "474327263": "provides children with a strong academic foundation through a bilingual curriculum",
    "460950114": "affirms a person's right to access quality medical care",
    "237338146": "provides social and educational services to help the elderly remain independent",
    "742513984": "creates urgent theater that embraces diverse communities in Austin, Texas",
    "271916249": "provides social and outreach services to the poor and homeless",
    "591950683": "inspires and entertains the community through exceptional theatrical experiences",
    # -- trailing word fixes --
    "870873558": "preserves Maine's working waterfront and marine heritage",
    "331212566": "promotes a people-friendly approach to fighting global poverty",
    "043602577": "helps low-income young people build their path to higher education",
    "911930327": "provides educational and social resources for underserved students in Marin City",
    "202905491": "provides services for families of children with special needs",
    "452208063": "promotes research and action to achieve sustainable change worldwide",
    "383167509": "supports and empowers children and families through strengths-based services",
    "060653185": "inspires and enables young people to recognize their full potential",
    "221641962": "enables young people to reach their full potential as responsible citizens",
    "237171151": "provides continuing education for certified public accountants in New York",
    "160743046": "provides book-lending and educational services to the local community",
}

# Sector label fixes (from fix_email_quality.py)
SECTOR_FIXES = {
    "animal-related": "animal welfare",
    "crime/legal": "legal services",
    "disease/disorder": "disease and disorder research",
    "food/agriculture": "food and agriculture",
    "mutual/membership": "community organizations",
    "social science": "social science research",
    "arts & culture": "arts and culture",
}

# ── CASE CONVERSION ──────────────────────────────────────────────────

# Words that should stay lowercase in sentence case
LOWERCASE_WORDS = {
    'a', 'an', 'and', 'as', 'at', 'but', 'by', 'for', 'in', 'nor',
    'of', 'on', 'or', 'so', 'the', 'to', 'up', 'via', 'with', 'yet',
    'its', 'our', 'who', 'whom', 'whose', 'that', 'which', 'from',
    'into', 'upon', 'than', 'vs', 'per', 'each',
}

# Words/acronyms that should stay uppercase
KEEP_UPPER = {
    'HIV', 'AIDS', 'STEM', 'LGBTQ', 'LGBTQIA', 'PTSD', 'ADHD', 'ALS',
    'CPR', 'GED', 'YMCA', 'YWCA', 'VA', 'US', 'USA', 'UK', 'DC', 'NYC',
    'IB', 'AP', 'SAT', 'ACT', 'ROTC', 'NFL', 'NBA', 'NCAA', 'CASA',
    'PK', 'K', 'NFP', 'CEO', 'IT', 'HVAC', 'EMT',
}


def to_sentence_case(text):
    """Convert ALL CAPS text to readable sentence case."""
    if not text or text != text.upper():
        return text  # Already mixed case, leave as-is

    words = text.split()
    result = []
    for i, word in enumerate(words):
        # Strip trailing punctuation for analysis
        stripped = word.rstrip('.,;:!?()"\'-/')
        lead = word[:len(word) - len(stripped)] if stripped != word else ''
        trail = word[len(stripped):] if stripped != word else ''
        # Actually lead should be punctuation at the start
        lead = ''
        trail = ''
        core = word
        # Split leading punctuation
        m = re.match(r'^([^A-Za-z0-9]*)(.+?)([^A-Za-z0-9]*)$', word)
        if m:
            lead, core, trail = m.group(1), m.group(2), m.group(3)
        else:
            core = word

        upper_core = core.upper()

        if upper_core in KEEP_UPPER:
            result.append(lead + upper_core + trail)
        elif i == 0:
            # First word: capitalize
            result.append(lead + core.capitalize() + trail)
        elif core.lower() in LOWERCASE_WORDS:
            result.append(lead + core.lower() + trail)
        elif len(core) <= 2 and core.isalpha():
            # Short words: lowercase
            result.append(lead + core.lower() + trail)
        else:
            # Regular word: lowercase
            result.append(lead + core.lower() + trail)

    return ' '.join(result)


# ── VERB CONJUGATION ─────────────────────────────────────────────────

GERUND_TO_3PS = {
    'providing': 'provides', 'promoting': 'promotes', 'supporting': 'supports',
    'serving': 'serves', 'helping': 'helps', 'creating': 'creates',
    'offering': 'offers', 'developing': 'develops', 'building': 'builds',
    'improving': 'improves', 'advancing': 'advances', 'fostering': 'fosters',
    'empowering': 'empowers', 'educating': 'educates', 'inspiring': 'inspires',
    'operating': 'operates', 'delivering': 'delivers', 'protecting': 'protects',
    'advocating': 'advocates', 'facilitating': 'facilitates', 'enabling': 'enables',
    'ensuring': 'ensures', 'enhancing': 'enhances', 'strengthening': 'strengthens',
    'connecting': 'connects', 'enriching': 'enriches', 'preparing': 'prepares',
    'working': 'works', 'assisting': 'assists', 'addressing': 'addresses',
    'raising': 'raises', 'training': 'trains', 'engaging': 'engages',
    'reducing': 'reduces', 'increasing': 'increases', 'producing': 'produces',
    'cultivating': 'cultivates', 'transforming': 'transforms',
    'preserving': 'preserves', 'restoring': 'restores', 'rescuing': 'rescues',
    'establishing': 'establishes', 'maintaining': 'maintains',
    'acquiring': 'acquires', 'conducting': 'conducts', 'seeking': 'seeks',
    'bringing': 'brings', 'making': 'makes', 'taking': 'takes',
    'giving': 'gives', 'leading': 'leads', 'meeting': 'meets',
    'running': 'runs', 'setting': 'sets', 'getting': 'gets',
    'putting': 'puts', 'keeping': 'keeps', 'holding': 'holds',
    'standing': 'stands', 'beginning': 'begins', 'showing': 'shows',
    'hearing': 'hears', 'playing': 'plays', 'moving': 'moves',
    'living': 'lives', 'believing': 'believes', 'organizing': 'organizes',
    'managing': 'manages', 'coordinating': 'coordinates',
    'implementing': 'implements', 'administering': 'administers',
    'combating': 'combats', 'eliminating': 'eliminates',
    'encouraging': 'encourages', 'nurturing': 'nurtures',
    'partnering': 'partners', 'collaborating': 'collaborates',
    'celebrating': 'celebrates', 'honoring': 'honors',
    'safeguarding': 'safeguards', 'securing': 'secures',
    'funding': 'funds', 'financing': 'finances',
    'caring': 'cares', 'mentoring': 'mentors',
    'counseling': 'counsels', 'healing': 'heals',
    'teaching': 'teaches', 'coaching': 'coaches',
    'guiding': 'guides', 'equipping': 'equips',
    'housing': 'houses', 'sheltering': 'shelters',
    'feeding': 'feeds', 'clothing': 'clothes',
    'uniting': 'unites', 'bridging': 'bridges',
    'alleviating': 'alleviates', 'mitigating': 'mitigates',
    'preventing': 'prevents', 'fighting': 'fights',
}

INFINITIVE_TO_3PS = {}
# Build from gerund map (most infinitives = 3ps minus 's')
# Plus direct list
for inf in [
    'provide', 'promote', 'support', 'serve', 'help', 'create', 'offer',
    'develop', 'build', 'improve', 'advance', 'foster', 'empower', 'educate',
    'inspire', 'operate', 'deliver', 'protect', 'advocate', 'facilitate',
    'enable', 'ensure', 'enhance', 'strengthen', 'connect', 'enrich',
    'prepare', 'work', 'assist', 'address', 'raise', 'train', 'engage',
    'reduce', 'increase', 'produce', 'cultivate', 'transform', 'preserve',
    'restore', 'rescue', 'encourage', 'equip', 'eliminate', 'eradicate',
    'prevent', 'instruct', 'sustain', 'maintain', 'extend', 'expand',
    'bring', 'make', 'take', 'give', 'lead', 'meet', 'run', 'set', 'get',
    'put', 'keep', 'hold', 'stand', 'begin', 'show', 'hear', 'play',
    'move', 'live', 'believe', 'organize', 'manage', 'coordinate',
    'implement', 'administer', 'combat', 'partner', 'collaborate',
    'celebrate', 'honor', 'safeguard', 'secure', 'fund', 'finance',
    'care', 'mentor', 'counsel', 'heal', 'teach', 'coach', 'guide',
    'house', 'shelter', 'feed', 'unite', 'bridge', 'alleviate',
    'mitigate', 'fight', 'acquire', 'conduct', 'seek', 'nurture',
    'clothe', 'excite', 'grow', 'own', 'collect', 'conserve',
    'furnish', 'receive', 'interpret',
]:
    if inf.endswith('ch') or inf.endswith('sh') or inf.endswith('ss') or inf.endswith('x'):
        INFINITIVE_TO_3PS[inf] = inf + 'es'
    elif inf.endswith('e'):
        INFINITIVE_TO_3PS[inf] = inf + 's'
    elif inf.endswith('y') and inf[-2] not in 'aeiou':
        INFINITIVE_TO_3PS[inf] = inf[:-1] + 'ies'
    else:
        INFINITIVE_TO_3PS[inf] = inf + 's'
# Manual overrides for irregular
INFINITIVE_TO_3PS['bring'] = 'brings'
INFINITIVE_TO_3PS['make'] = 'makes'
INFINITIVE_TO_3PS['take'] = 'takes'
INFINITIVE_TO_3PS['give'] = 'gives'
INFINITIVE_TO_3PS['have'] = 'has'
INFINITIVE_TO_3PS['do'] = 'does'

# Trailing words that indicate truncation
TRAILING_WORDS = {
    'and', 'the', 'a', 'an', 'of', 'for', 'to', 'in', 'or', 'with',
    'that', 'by', 'on', 'at', 'from', 'through', 'its', 'their', 'who',
    'which', 'both', 'all', 'as', 'but', 'into', 'including', 'such',
    'between', 'within', 'throughout', 'among', 'our', 'each', 'every',
    'this', 'those', 'these', 'regardless', 'thereby', 'whereas',
    'so', 'nor', 'yet', 'while',
    # Adjectives that indicate truncation when trailing
    'diverse', 'various', 'innovative', 'creative', 'classical', 'social',
    'emotional', 'cultural', 'educational', 'professional', 'personal',
    'physical', 'mental', 'spiritual', 'traditional', 'national',
    'international', 'local', 'regional', 'special', 'unique',
}

# Words that are almost always verbs (not nouns) after "and" or ","
VERB_ONLY = {
    'protect', 'prevent', 'facilitate', 'sustain', 'operate', 'deliver',
    'empower', 'enable', 'inspire', 'promote', 'enhance', 'advance',
    'improve', 'establish', 'provide', 'develop', 'create', 'manage',
    'preserve', 'restore', 'educate', 'maintain', 'cultivate', 'transform',
    'strengthen', 'connect', 'enrich', 'prepare', 'encourage', 'equip',
    'eliminate', 'eradicate', 'foster', 'interpret', 'ensure', 'engage',
    'implement', 'coordinate', 'administer', 'expand', 'extend',
    'organize', 'collaborate', 'celebrate', 'secure', 'finance',
    'heal', 'alleviate', 'mitigate', 'fight', 'combat', 'reduce',
    'increase', 'produce', 'acquire', 'nurture', 'safeguard',
    'unite', 'clothe', 'excite', 'conserve', 'receive', 'deliver',
}


def fix_verb_agreement(text):
    """Fix 'Xes and Y' patterns where Y is a bare infinitive verb."""
    if not text:
        return text
    words = text.split()
    if not words:
        return text
    first = words[0].rstrip('.,;:').lower()
    known_3ps = set(INFINITIVE_TO_3PS.values())
    if first not in known_3ps:
        return text
    result = []
    i = 0
    while i < len(words):
        word = words[i]
        clean = word.rstrip('.,;:').lower()
        trail = word[len(word.rstrip('.,;:')):]
        if clean == 'and' and i + 1 < len(words):
            nw = words[i + 1]
            nc = nw.rstrip('.,;:').lower()
            nt = nw[len(nw.rstrip('.,;:')):]
            if nc in VERB_ONLY and nc in INFINITIVE_TO_3PS:
                result.append(word)
                result.append(INFINITIVE_TO_3PS[nc] + nt)
                i += 2
                continue
        if i > 0 and clean in VERB_ONLY and clean in INFINITIVE_TO_3PS:
            prev = words[i - 1]
            if prev.endswith(','):
                result.append(INFINITIVE_TO_3PS[clean] + trail)
                i += 1
                continue
        result.append(word)
        i += 1
    return ' '.join(result)


US_STATES = {
    'alabama': 'Alabama', 'alaska': 'Alaska', 'arizona': 'Arizona',
    'arkansas': 'Arkansas', 'california': 'California', 'colorado': 'Colorado',
    'connecticut': 'Connecticut', 'delaware': 'Delaware', 'florida': 'Florida',
    'georgia': 'Georgia', 'hawaii': 'Hawaii', 'idaho': 'Idaho',
    'illinois': 'Illinois', 'indiana': 'Indiana', 'iowa': 'Iowa',
    'kansas': 'Kansas', 'kentucky': 'Kentucky', 'louisiana': 'Louisiana',
    'maine': 'Maine', 'maryland': 'Maryland', 'massachusetts': 'Massachusetts',
    'michigan': 'Michigan', 'minnesota': 'Minnesota', 'mississippi': 'Mississippi',
    'missouri': 'Missouri', 'montana': 'Montana', 'nebraska': 'Nebraska',
    'nevada': 'Nevada', 'ohio': 'Ohio', 'oklahoma': 'Oklahoma',
    'oregon': 'Oregon', 'pennsylvania': 'Pennsylvania', 'tennessee': 'Tennessee',
    'texas': 'Texas', 'utah': 'Utah', 'vermont': 'Vermont',
    'virginia': 'Virginia', 'washington': 'Washington', 'wisconsin': 'Wisconsin',
    'wyoming': 'Wyoming',
    'new hampshire': 'New Hampshire', 'new jersey': 'New Jersey',
    'new mexico': 'New Mexico', 'new york': 'New York',
    'north carolina': 'North Carolina', 'north dakota': 'North Dakota',
    'south carolina': 'South Carolina', 'south dakota': 'South Dakota',
    'west virginia': 'West Virginia', 'rhode island': 'Rhode Island',
    'district of columbia': 'District of Columbia', 'puerto rico': 'Puerto Rico',
    'new york city': 'New York City',
}


def capitalize_states(text):
    """Capitalize US state names in text."""
    if not text:
        return text
    result = text
    for lower, proper in sorted(US_STATES.items(), key=lambda x: -len(x[0])):
        pattern = r'\b' + re.escape(lower) + r'\b'
        result = re.sub(pattern, proper, result, flags=re.IGNORECASE)
    return result


# ── MAIN EXTRACTION ──────────────────────────────────────────────────

def extract_mission_short(raw_mission, org_name="", max_len=80):
    """
    Extract a clean third-person verb phrase from a mission description.
    """
    if not raw_mission:
        return ""

    # Step 0: Normalize
    text = re.sub(r'\s+', ' ', raw_mission).strip()
    text = re.sub(r'continued on schedule o.*', '', text, flags=re.IGNORECASE).strip()
    text = re.sub(r'see schedule o.*', '', text, flags=re.IGNORECASE).strip()
    text = re.sub(r'\(the "?organization"?\)', '', text, flags=re.IGNORECASE).strip()

    # Step 1: Convert ALL CAPS to sentence case
    text = to_sentence_case(text)

    # Step 2: Strip preambles (order matters - most specific first)
    # Build org name variants for stripping
    org_variants = set()
    if org_name:
        org_variants.add(org_name.strip())
        no_suffix = re.sub(r'\s+(INC|LLC|CORP|LTD|CO|NFP|NPC)\.?\s*$', '', org_name, flags=re.IGNORECASE).strip()
        org_variants.add(no_suffix)
        # Also the version from the mission text
        for ov in list(org_variants):
            org_variants.add(ov.lower())
            org_variants.add(ov.upper())
            org_variants.add(ov.title())

    preamble_patterns = [
        # "[Org name]'s mission is to..."
        # "[Org name] is a ... that/which..."
        # "[Org name] was founded/created/established to..."
        # "The mission of [org] is to..."
        # "Our/Its/The primary mission/purpose is to..."
        # "We exist/strive/seek/aim to..."
        # "The organization/corporation ..."
        # "Founded in YYYY, ..."
        # "As a non-profit 501(c)(3) organization, ..."
        r"(?:the\s+)?(?:primary\s+)?(?:main\s+)?(?:purpose|mission|goal|aim|objective)\s+(?:of\s+(?:the\s+)?[\w\s&\'\-\.\,]+?\s+)?is\s+to\s+",
        r"(?:our|its|the)\s+(?:primary\s+)?(?:main\s+)?(?:mission|purpose|goal)\s+is\s+to\s+",
        r"(?:we|the\s+organization|the\s+corporation|the\s+foundation|the\s+association)\s+(?:exist|exists|strive|strives|seek|seeks|aim|aims|work|works)\s+to\s+",
        r"(?:we|the\s+organization)\s+(?:are|is)\s+(?:committed|dedicated|devoted)\s+to\s+",
        r"(?:it\s+is\s+our\s+miss?ion\s+to\s+)",
        r"(?:founded|established|created|organized|formed|incorporated)\s+(?:in\s+\d{4}\s*,?\s*)?(?:to\s+|for\s+the\s+purpose\s+of\s+)",
        r"as\s+a\s+(?:non-?profit|not-for-profit|501\(c\)\(3\))[\w\s,\-]*?(?:organization|entity|corporation)[\w\s,\-]*?,\s*",
        r"(?:the\s+)?(?:organization|corporation|foundation|association|company|entity)\s+(?:is\s+)?(?:was\s+)?(?:formed|created|organized|established|operated|incorporated)\s+(?:exclusively\s+)?(?:to|for\s+the\s+purpose\s+of)\s+",
    ]

    working = text

    # First try to strip org name from the beginning
    for ov in sorted(org_variants, key=len, reverse=True):
        if working.lower().startswith(ov.lower()):
            working = working[len(ov):].strip()
            # Strip possessive
            if working.startswith("'s "):
                working = working[3:].strip()
                # "mission is to..."
                m = re.match(r"(?:primary\s+)?(?:mission|purpose|goal)\s+is\s+to\s+", working, re.IGNORECASE)
                if m:
                    working = working[m.end():]
            break

    # Then try preamble patterns
    for p in preamble_patterns:
        m = re.match(p, working, re.IGNORECASE)
        if m:
            working = working[m.end():]
            break

    # Strip "is a/an [type] that/which/dedicated to" pattern
    m = re.match(r"is\s+(?:a|an)\s+[\w\s,\-\(\)]+?(?:organization|nonprofit|charity|group|center|programme?|agency|foundation|association|club|school|ministry|shelter|coalition|institute|company|firm|corporation)\s+(?:that|which|dedicated to|committed to|working to|focused on|designed to|created to|established to|formed to)\s+", working, re.IGNORECASE)
    if m:
        working = working[m.end():]

    # Strip another common pattern: "envisions a community where..."
    m = re.match(r"envisions?\s+", working, re.IGNORECASE)
    if m:
        working = "creates " + working[m.end():]

    working = working.strip()

    # Step 2b: Aggressive cleanup for remaining preamble patterns
    # Strip "to " prefix and convert infinitive
    if working.lower().startswith('to '):
        working = working[3:].strip()

    # Strip "the organization/corporation/entity..." patterns
    working = re.sub(r"^the\s+organization'?s?\s+(?:primary\s+)?(?:mission|purpose|goal)\s+is\s+(?:to\s+)?", '', working, flags=re.IGNORECASE).strip()
    working = re.sub(r"^the\s+(?:organization|corporation|entity|foundation|company)\s+(?:is\s+)?(?:was\s+)?(?:formed|created|organized|established|operated|incorporated|dedicated|committed|designed|a\s+)?\s*(?:to\s+|for\s+)?", '', working, flags=re.IGNORECASE).strip()

    # Strip "[org name] is a/an ... that/which/dedicated to..."
    for ov in sorted(org_variants, key=len, reverse=True):
        pat = re.escape(ov) + r"[\s',]*(?:is|are|was)\s+(?:a|an)\s+[\w\s,\-\(\)]+?(?:that|which|dedicated to|committed to|working to|focused on|designed to|created to|established to|formed to)\s+"
        m = re.match(pat, working, re.IGNORECASE)
        if m:
            working = working[m.end():]
            break
        # Also: "[org name]'s mission is to..."
        pat2 = re.escape(ov) + r"[\s']*(?:'s\s+)?(?:primary\s+)?(?:mission|purpose|goal)\s+is\s+(?:to\s+)?"
        m = re.match(pat2, working, re.IGNORECASE)
        if m:
            working = working[m.end():]
            break
        # Also: simple "[org name] verb..."
        if working.lower().startswith(ov.lower()):
            rest = working[len(ov):].strip()
            if rest and rest.split()[0].lower().rstrip('s') in INFINITIVE_TO_3PS:
                working = rest
                break

    # Strip remaining "the [proper noun phrase] is/provides/etc" where proper noun = org name
    m = re.match(r"^the\s+[\w\s&\'\-\.]+?\s+(is|provides|promotes|supports|serves|helps|creates|offers|develops|builds|improves|advances|fosters|empowers|educates|inspires|operates|delivers|protects|advocates|facilitates|enables|ensures|enhances|strengthens|connects|enriches|prepares|works|assists|addresses|raises|trains|engages|reduces|increases|produces|cultivates|transforms|preserves|restores|rescues)\s+", working, re.IGNORECASE)
    if m:
        # Check if the matched text contains the org name
        matched_text = working[:m.start(1)].lower()
        for ov in org_variants:
            if ov.lower() in matched_text:
                working = working[m.start(1):]
                break

    working = working.strip()

    # Strip "is a/an ... that/which/dedicated to" at the start (no org name)
    m = re.match(r"^is\s+(?:a|an)\s+[\w\s,\-\(\)]+?(?:organization|nonprofit|charity|group|center|programme?|agency|foundation|association|club|school|ministry|shelter|coalition|institute|company|firm|corporation)\s+(?:that|which|dedicated to|committed to|working to|focused on|designed to|created to|established to|formed to)\s+", working, re.IGNORECASE)
    if m:
        working = working[m.end():]

    # Strip "is a non-profit..." / "is a private, not-for-profit..."
    m = re.match(r"^(?:is|are|was)\s+(?:a\s+)?(?:private[,\s]*)?(?:non-?profit|not-for-profit|501\(c\)\(3\)|tax-exempt)[\w\s,\-]*?(?:organization|entity|corporation|institution|company)[\w\s,\-]*?(?:that|which|dedicated to|committed to)\s+", working, re.IGNORECASE)
    if m:
        working = working[m.end():]

    # Final "to " strip after all preamble work
    if working.lower().startswith('to '):
        working = working[3:].strip()

    # Step 2c: Strip leading punctuation and org suffixes (INC/LLC fragments)
    working = re.sub(r"^[,.\s;:'\"()\-]+", '', working).strip()
    working = re.sub(r"^(?:inc|llc|corp|ltd|co|nfp|npc)\.?,?\s*", '', working, flags=re.IGNORECASE).strip()
    working = re.sub(r"^[,.\s;:'\"()\-]+", '', working).strip()
    # Also strip common preamble fragments left after org suffix removal
    working = re.sub(r'^(?:\(?(?:the\s+)?"?(?:association|corporation|foundation|organization|company|college|center)"?\)?\s*)', '', working, flags=re.IGNORECASE).strip()
    working = re.sub(r"^[,.\s;:'\"()\-]+", '', working).strip()
    # Strip "is a/an..." preamble if still present
    m = re.match(r"^(?:is|are|was)\s+(?:a|an)\s+[\w\s,\-\(\)\"]+?(?:that|which|dedicated to|committed to|working to|focused on|designed to|created to|established to|formed to|incorporated to)\s+", working, re.IGNORECASE)
    if m:
        working = working[m.end():]
    # Strip "is a/an [type]" without connector
    m = re.match(r"^(?:is|are|was)\s+(?:a|an)\s+(?:non-?profit|not-for-profit|501\(c\)\(?3?\)?\(?3?\)?|tax-exempt|charitable|public|private|community)[,\s\-]+(?:organization|entity|corporation|institution|company|pharmacy|foundation|association|school|ministry)[\s,]*(?:that|which|dedicated|committed|working|focused|designed|created|established|formed|incorporated)?[\s,]*(?:to\s+)?", working, re.IGNORECASE)
    if m:
        working = working[m.end():]
    working = re.sub(r"^[,.\s;:'\"()\-]+", '', working).strip()

    # Step 3: Convert to third-person singular verb
    if not working:
        return ""

    first_word = working.split()[0]
    first_lower = first_word.lower().rstrip('.,;:')

    # Gerund -> 3ps
    if first_lower in GERUND_TO_3PS:
        working = GERUND_TO_3PS[first_lower] + working[len(first_word):]
    # Infinitive -> 3ps
    elif first_lower in INFINITIVE_TO_3PS:
        working = INFINITIVE_TO_3PS[first_lower] + working[len(first_word):]

    working = working.strip()

    # Step 4: Find natural breakpoint
    if len(working) <= max_len:
        result = working
    else:
        best = ""

        # Try first sentence
        sentences = re.split(r'(?<=[.!])\s+', working)
        if sentences and len(sentences[0].rstrip('.')) <= max_len and len(sentences[0].rstrip('.')) >= 20:
            best = sentences[0].rstrip('.')

        # Try semicolon
        if not best:
            parts = working.split(';')
            if parts and len(parts[0].strip()) <= max_len and len(parts[0].strip()) >= 20:
                best = parts[0].strip()

        # Try comma boundary (last comma before max_len)
        if not best:
            for pos in [m.start() for m in re.finditer(r',\s', working)]:
                candidate = working[:pos].strip()
                if len(candidate) <= max_len and len(candidate) >= 20:
                    best = candidate  # keep going to find later comma
                elif len(candidate) > max_len:
                    break

        # Try "and" boundary
        if not best:
            for pos in [m.start() for m in re.finditer(r'\s+and\s+', working)]:
                candidate = working[:pos].strip().rstrip(',')
                if len(candidate) <= max_len and len(candidate) >= 20:
                    best = candidate
                elif len(candidate) > max_len:
                    break

        # Last resort: word boundary
        if not best:
            words = working.split()
            candidate = ""
            for w in words:
                test = (candidate + " " + w).strip() if candidate else w
                if len(test) > max_len:
                    break
                candidate = test
            best = candidate

        result = best

    # Step 5: Clean up
    # Remove trailing prepositions/articles
    words = result.split()
    while words and words[-1].rstrip('.,;:').lower() in TRAILING_WORDS:
        words.pop()
    result = ' '.join(words)

    # Remove trailing punctuation
    result = result.rstrip('.,;:!?')

    # Ensure starts with lowercase (follows "I saw that {Org}")
    if result:
        # Don't lowercase acronyms
        if not re.match(r'^[A-Z]{2,}', result):
            result = result[0].lower() + result[1:]

    # Fix ampersands
    result = result.replace(' & ', ' and ')

    # Fix common misspellings
    fixes = {
        'moutaineering': 'mountaineering', 'nutures': 'nurtures',
        'opportuniy': 'opportunity', 'opportunitites': 'opportunities',
        'kindergarden': 'kindergarten', 'thier': 'their',
        'childern': 'children', 'perserve': 'preserve',
        'couseling': 'counseling', 'misssion': 'mission',
    }
    for wrong, right in fixes.items():
        result = result.replace(wrong, right)

    result = re.sub(r'\s+', ' ', result).strip()
    return result


# ── TEMPLATE ─────────────────────────────────────────────────────────

TEMPLATE_C_BODY = """{greeting_line}

My name is Alec and I'm with a company called TheGrantScout. I saw that {organization_name} {mission_short} and wanted to see if we can help you find private foundation funding.

Let me know if you're open to a quick call!

Alec Kleinman
TheGrantScout
740 E, 2320 N, Provo, UT 84604

P.S - If this isn't relevant just let me know and I won't reach out again."""


def main():
    # Load CSV
    with open(CSV_IN) as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        all_rows = list(reader)

    # Load missions from DB
    tc_eins = [r['prospect_ein'] for r in all_rows if r['template_used'] == 'C']
    conn = psycopg2.connect(host='localhost', port=5432, database='thegrantscout',
                            user='postgres', password='postgres')
    cur = conn.cursor()
    cur.execute("""
        SELECT ein, mission_description
        FROM f990_2025.nonprofits_prospects2
        WHERE ein = ANY(%s) AND mission_description IS NOT NULL
    """, (tc_eins,))
    missions = {row[0]: row[1] for row in cur.fetchall()}

    # Also get org names from DB (better quality than CSV)
    cur.execute("""
        SELECT ein, organization_name
        FROM f990_2025.nonprofits_prospects2
        WHERE ein = ANY(%s)
    """, (tc_eins,))
    db_org_names = {row[0]: row[1] for row in cur.fetchall()}
    conn.close()

    # Process
    changed = 0
    override_count = 0

    for row in all_rows:
        if row['template_used'] != 'C':
            # Fix sector labels for Template A
            sl = row.get('sector_label', '')
            if sl in SECTOR_FIXES:
                new_sector = SECTOR_FIXES[sl]
                if new_sector:
                    old_subj = row['subject_line']
                    state = old_subj.rsplit(' in ', 1)[1] if ' in ' in old_subj else ''
                    row['subject_line'] = f"Private funders for {new_sector} in {state}"
                    row['sector_label'] = new_sector
            continue

        ein = row['prospect_ein']
        org = row['organization_name']
        db_org = db_org_names.get(ein, org)

        # Check manual override first
        if ein in MANUAL_OVERRIDES:
            new_ms = MANUAL_OVERRIDES[ein]
            override_count += 1
        else:
            mission = missions.get(ein, '')
            new_ms = extract_mission_short(mission, db_org)
            new_ms = fix_verb_agreement(new_ms)

        new_ms = capitalize_states(new_ms)
        old_ms = row.get('mission_short', '')
        if new_ms != old_ms:
            changed += 1

        row['mission_short'] = new_ms

        # Clean org name for email body (strip INC/LLC)
        org_clean = re.sub(r'\s+(INC|LLC|CORP|LTD|CO|NFP|NPC)\.?\s*$', '', org, flags=re.IGNORECASE).strip()

        # Regenerate body
        gname, _ = resolve_greeting(
            row.get('contact_first_name'), row.get('contact_email')
        )
        row['email_body'] = TEMPLATE_C_BODY.format(
            greeting_line=format_greeting_line(gname),
            organization_name=org_clean,
            mission_short=new_ms,
        )

    # Write
    with open(CSV_OUT, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_rows)

    print(f"=== REGENERATION COMPLETE ===")
    print(f"Template C processed: {len(tc_eins)}")
    print(f"Mission_shorts changed: {changed}")
    print(f"Manual overrides: {override_count}")

    # Dump for review
    with open('/tmp/tc_new_missions.txt', 'w') as f:
        for row in all_rows:
            if row['template_used'] == 'C':
                org_clean = re.sub(r'\s+(INC|LLC|CORP|LTD|CO|NFP|NPC)\.?\s*$', '', row['organization_name'], flags=re.IGNORECASE).strip()
                f.write(f"{row['prospect_ein']}|I saw that {org_clean} {row['mission_short']} and wanted to see if we can help\n")


if __name__ == '__main__':
    main()
