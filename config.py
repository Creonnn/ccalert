import aiolimiter

class Config:
    db_path = "cc_alert.db"

    limiter = aiolimiter.AsyncLimiter(5, 1)  # 5 requests per second
    timeout = 10
    log_channel_id = 1340210498968489984
    command_channel_id = 1341790452344557729

    truncate_patterns = r"geforce|rtx|16gb|gddr7|graphics|card|32gb|,|2482 Mhz|PCI-E 5.0|256 bit|16-pin x 1|\
        HDMI 2.1b x 1|Display Port 2.1b x 3|DLSS 4|with|gddr6|amd|radeon|edition|rx|12gb|32g|16g|PRIME-9070-O16G|\
        TUF-9070-O16G-GAMING|12g"

    alert_channel_id = {
    '5090': 1337248336909963275,
    '5080': 1337248379595526144,
    '5070 Ti': 1342270436410523668,
    '5070': 1347084732743155744,
    '9070 XT': 1347084761742577705,
    '9070': 1347084781921505281
    }

    spam_channel_id = {
        '5080': 1336767991269822607,
        '5090': 1337128522195402895
        #'5070 Ti': 1342270404990996581
    }
    cc_roles = {
    'Brampton': 1336847038620499988,
    'Mississauga': 1336847097063800934,
    'Etobicoke': 1336847139812147311,
    'Vaughan': 1336847239825326120,
    'Toronto Down Town 284': 1336847274734518354,
    'North York': 1336847398105780245,
    'Oakville': 1336847453713989725,
    'Richmond Hill': 1336847495971471380,
    'Markham Unionville': 1336847565827604522,
    'Burlington': 1336847618717778032,
    'Toronto Kennedy': 1336847684618686464,
    'Newmarket': 1336847748527558686,
    'Hamilton': 1336847782345965779,
    'Ajax': 1336847820766052443,
    'Cambridge': 1336847861186560020,
    'Waterloo': 1336847900314959882,
    'Barrie': 1336847932569161791,
    'Whitby': 1336847964030894122,
    'St Catharines': 1336848001989083208,
    'Oshawa': 1336848054481059880,
    'London Masonville': 1336848088320704634,
    'Kingston': 1336848156645789797,
    'Kanata': 1336848251642449920,
    'Ottawa Merivale': 1336848296404320320,
    'Ottawa Downtown': 1336848350976151592,
    'Ottawa Orleans': 1336848395817455646,
    'Gatineau': 1336848452793139302,
    'West Island': 1336848498372382750,
    'Laval': 1336848537203380325,
    'Marche Central': 1336848570854412378,
    'Montreal': 1336848610997960724,
    'Brossard': 1336848656581787658,
    'QC Vanier': 1336848690744131635,
    'Halifax': 1336848739544862781,
    'Coquitlam': 1336848774437277756,
    'Surrey': 1336848835712127128,
    'Burnaby': 1336848862698143794,
    'Vancouver Broadway': 1336848921720258600,
    'Richmond': 1336848974161776701,
    'Online': 1345146046912794644
}