import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import io

# --- 1. Page Configuration ---
st.set_page_config(
    page_title="LestariLens Intelligence",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. Safe Global CSS for Premium UI ---
st.markdown("""
<style>
    /* Main Backgrounds */
    [data-testid="stAppViewContainer"] { background-color: #F7F5F0 !important; font-family: 'Inter', sans-serif; }
    [data-testid="stSidebar"] { background-color: #EBE8DE !important; border-right: 1px solid #DEDAD0; }
    [data-testid="stHeader"] { display: none !important; }
    
    .block-container { padding-top: 2.5rem !important; max-width: 1400px !important; }
    h1, h2, h3 { color: #2D3142 !important; font-weight: 600 !important; margin-top:0; padding-top:0;}
    .sub-header { color: #E27D60; font-size: 0.85rem; text-transform: uppercase; font-weight: 700; margin-bottom: -15px; letter-spacing: 1px;}

    /* Force all bordered containers to be crisp white */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #FFFFFF !important;
        border-radius: 12px !important;
        box-shadow: 0 2px 6px rgba(0,0,0,0.03) !important;
        border: 1px solid #EAE6DB !important;
    }

    /* Metric Cards Override */
    [data-testid="stMetricValue"] { color: #2D3142 !important; font-weight: 700 !important; }
    [data-testid="stMetricLabel"] { color: #888C95 !important; font-weight: 600 !important; }

    /* Button Styling */
    .stButton>button { border-radius: 8px !important; font-weight: bold !important; transition: 0.2s; border: none !important; }
    button[kind="primary"] { background-color: #E27D60 !important; color: white !important; }
    button[kind="secondary"] { background-color: #85A88F !important; color: white !important; border-radius: 20px !important; }
    button[kind="primary"]:hover { background-color: #D36C4F !important; }
    button[kind="secondary"]:hover { background-color: #72967C !important; }
    
    /* Sleek Navigation Menu */
    [data-testid="stSidebar"] div[role="radiogroup"] > label > div:first-child { display: none; }
    [data-testid="stSidebar"] div[role="radiogroup"] > label {
        padding: 10px 15px; border-radius: 8px; margin-bottom: 5px; background-color: transparent; transition: 0.2s all; cursor: pointer;
    }
    [data-testid="stSidebar"] div[role="radiogroup"] > label:hover { background-color: rgba(0,0,0,0.05); }
    [data-testid="stSidebar"] div[role="radiogroup"] > label[data-checked="true"] {
        background-color: #FFFFFF; box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    [data-testid="stSidebar"] div[role="radiogroup"] > label[data-checked="true"] p {
        color: #E27D60 !important; font-weight: 700 !important;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. Data Loading ---
@st.cache_data
def load_data():
    csv_data = """state,year,visitors_000,log_population,log_gdp_total,log_gdp_services,services_share,log_gdp_per_capita,log_rooms,rooms_per_1k_residents,log_lf_employed,u_rate,p_rate,cpi_accom_food_rel,cpi_recreation_rel
Johor,2017,13140.6397344478,8.215276958936633,11.72449288669644,11.002084041079417,0.4855811559874232,10.416971206741946,10.366938509842946,8.599134433324316,7.39186211384821,3.4,67.1,1.0142987627667526,1.0292468099521965
Kedah,2017,13304.534929663,7.670381879311885,10.670502638936183,10.077784834107018,0.5528227767687072,9.907876038606435,9.491828300264636,6.180792014552917,6.816215482341622,2.825,65.0,0.9927094577763016,1.01208265893778
Kelantan,2017,9623.66382258783,7.511524648390866,10.064805698882292,9.674013317161135,0.6765205995019399,9.461036329473563,8.38022733634308,2.3838162930563147,6.5190735389083185,3.525,61.3,0.9273436851282902,0.9649565250122333
Melaka,2017,12624.984812844,6.8168454036222945,10.617172041428429,9.831630314809079,0.4558726765176947,10.708081916788272,9.801177933711559,19.77329974811083,6.010592927542981,1.0,65.425,0.9889230258241302,1.0141905371325328
Negeri Sembilan,2017,10822.3205520833,7.01571242048723,10.687748141489163,9.94825783828611,0.4773571609409945,10.57979099998407,9.163458386076051,8.565529622980252,6.17882546828242,2.825,65.375,0.9840073071493813,1.0132871607633531
Pahang,2017,16491.3391442,7.4067107301776405,10.907626859185362,10.193150711339838,0.4894484432720848,10.408671407989857,10.150386692204734,15.544019429265331,6.541354621818951,2.925,65.5,0.9518558498712946,0.9605902058945308
Perak,2017,20109.7100671475,7.821322304934696,11.146727766040453,10.669599559250166,0.620562963807368,10.233160740087895,9.708141544619421,6.598347505214183,6.917284729198267,3.9,63.075,0.993838744498879,0.9779049196371439
Perlis,2017,1413.61053340025,5.529429087511423,8.647282065367014,8.222250155186247,0.6537489235506743,10.025608256837726,7.126890808898808,4.940476190476191,4.590817679763691,3.4,59.925,0.985003736610479,0.9846802424059925
Pulau Pinang,2017,12642.6432832667,7.463993942274623,11.37099112915621,10.679551959226117,0.5008547350554133,10.814752465863723,10.051260796825561,13.293389140530934,6.715504591110298,2.025,67.625,1.031238063605414,0.9911544397184476
Sabah,2017,17791.7126417,8.257359721784196,11.336107817838867,10.475417156149309,0.4228699213828149,9.986503375036808,10.060576767778903,6.069140797219845,7.485239050888359,5.95,68.0,1.043062359877107,1.0545413482892312
Sarawak,2017,17670.3474462916,7.925265966213205,11.776585873695101,10.681463193840067,0.33449856819549,10.759075186464033,9.922652721797139,7.369771897480389,7.136880901973894,3.05,67.95,0.9733787262310055,0.946136183987654
Terengganu,2017,12979.3763672308,7.0967213784947605,10.433484928167648,9.736033465155268,0.49785248384738645,10.244518828655025,9.288134399416203,8.947847682119205,6.082390128594483,4.975,60.475,0.9187743917628497,0.9596868295253511
W.P. Kuala Lumpur,2017,19049.4424775752,7.491757012281284,12.23648209072676,12.101798045607932,0.8739920101101146,11.652480357427613,10.727136541160231,25.416016060673655,6.742113832439381,3.075,68.875,1.0278502034376815,1.0095983739225354
W.P. Labuan,2017,381.004767748,4.580877493419047,8.823177648716,8.535537697346431,0.7500315914769878,11.15005543427909,7.436617265234227,17.387295081967213,3.649358695951653,8.3,63.275,1.0125051897367765,1.0714796552113526
Johor,2018,13487.2379119749,8.22935110616309,11.77978687135016,11.07289697070501,0.4931756399970916,10.458191044169206,10.366938509842946,8.478956633061289,7.445315331850737,2.95,69.475,1.0293686058030227,1.0305733870090306
Kedah,2018,14480.018395565,7.679251425953058,10.710048905820353,10.130788808604764,0.5603127902235143,9.938552758849431,9.491828300264636,6.12621359223301,6.817639087039028,2.9,63.675,0.9911585904713363,1.00680722635092
Kelantan,2018,9846.1234357734,7.528600547786677,10.091736963169414,9.724428228868762,0.692595783957969,9.470891694364873,8.38022733634308,2.3434560601988714,6.529747251481985,4.475,60.725,0.9276944514092409,0.9628322602924411
Melaka,2018,13122.6041634891,6.826978968954849,10.654329679365642,9.889931381447926,0.4656140076224397,10.73510598939293,9.801177933711559,19.57393755420642,6.037094962620542,1.325,66.9,0.9950387813569981,1.0178577341728439
Negeri Sembilan,2018,12802.1189060886,7.023669903578493,10.7297231526225,10.004517570107602,0.48422501052653694,10.613808528026142,9.163458386076051,8.497640039184255,6.191697646839086,3.25,65.925,0.9790576561838488,1.0214907778403257
Pahang,2018,18111.3565763172,7.417400205999965,10.938271112548817,10.256042445709896,0.5054891691126336,10.42862618553099,10.150386692204734,15.378746921367213,6.578903929492285,2.55,66.725,0.9519620859314308,0.9611671152781786
Perak,2018,17553.1612058818,7.825445031769999,11.198636685884976,10.734455662488964,0.6286497438546828,10.280946933097114,9.708141544619421,6.571200319552626,6.946013991099227,3.3,63.525,0.9924739094156284,0.9784997611084567
Perlis,2018,2155.5079034032,5.535363823031238,8.680223869948136,8.263883946239012,0.6594560676281026,10.052615325899035,7.126890808898808,4.911242603550296,4.665088676199335,3.725,64.425,0.9801099113392824,0.9862199789018558
Pulau Pinang,2018,14450.4911905341,7.474658732967832,11.421185489395492,10.739012468690463,0.5055172984132545,10.854282035409797,10.051260796825561,13.152371227592466,6.725363719738068,2.2,67.65,1.0319334777443925,0.9956053417095174
Sabah,2018,20359.8810907898,8.268321491529296,11.350547890187288,10.53004202355744,0.44020891117321576,9.989981677640127,10.060576767778903,6.002975579725015,7.518240700144822,5.949999999999999,68.875,1.0481776667064002,1.0530528447015748
Sarawak,2018,19380.2301990599,7.93440600825238,11.798178261619444,10.7431667933744,0.3481884341730159,10.7715275323492,9.922652721797139,7.302718773507182,7.156722510305805,3.175,68.275,0.9793207199727071,0.949965230636776
Terengganu,2018,13742.3663642652,7.113386378545049,10.458469994511574,9.771516827150979,0.5031066178834457,10.252838894948663,9.288134399416203,8.799967434665799,6.108469502360524,4.85,60.4,0.9203944312684196,0.956550122284087
W.P. Kuala Lumpur,2018,19165.4971713709,7.489970898834801,12.303013195558387,12.172889840666521,0.8779871202340959,11.720797575705724,10.727136541160231,25.46145251396648,6.7046900522502355,2.4,67.475,1.0296974355390958,1.0096833859210097
W.P. Labuan,2018,544.932022066991,4.59511985013459,8.88805871117435,8.609002158212215,0.7564971198523218,11.200694140021897,7.436617265234227,17.141414141414142,3.7293013686128518,4.725,63.875,1.0093757578497826,1.0690987875662865
Johor,2019,14274.0,8.232493334402921,11.807279763532323,11.13570842668265,0.5109051426409104,10.482541708111539,10.366938509842946,8.452355631181538,7.469440353038936,2.75,70.175,1.0376322899104187,1.0337651624514894
Kedah,2019,14831.0,7.68418606367882,10.754518415163712,10.17833203714186,0.5620376839627866,9.978087630467028,9.491828300264636,6.096057413626536,6.827277059820571,3.025,63.224999999999994,1.0000609396900202,1.015392114587825
Kelantan,2019,10986.0,7.5410462923887165,10.14561684856917,9.771975034897084,0.688223379890827,9.51232583516259,8.38022733634308,2.3144707506104685,6.525542722684123,4.875,59.225,0.9257632696175019,0.9618478036708599
Melaka,2019,13979.0,6.833462674400282,10.682431554061052,9.948352738331455,0.4799473753732414,10.756724158642907,9.801177933711559,19.44743644980612,6.064017739789691,1.55,67.975,0.9875154888378801,1.0156170906841149
Negeri Sembilan,2019,13303.0,7.026604412820518,10.779655087340874,10.087365106471742,0.500428783595734,10.660805953502493,9.163458386076051,8.472740188243652,6.20050917404269,2.55,65.425,0.9783501594588555,1.0328652580663304
Pahang,2019,18498.0,7.421416877567336,10.97565955732568,10.316161315744827,0.5171107340727474,10.461997958740481,10.150386692204734,15.317099437597223,6.585343726009258,2.8,66.625,0.9415588372707143,0.960347963028928
Perak,2019,21070.0,7.827559830156089,11.238392667296804,10.778343477158655,0.6312525933409294,10.318588116122852,9.708141544619421,6.557318239795918,6.94812917312041,4.35,64.15,0.9842003697007861,0.9767712180580813
Perlis,2019,2088.0,5.537334267018537,8.724424247847972,8.312607129790916,0.6624454142792441,10.094845259811574,7.126890808898808,4.9015748031496065,4.695696212687462,3.625,65.19999999999999,0.9780251477787482,1.011567520950899
Pulau Pinang,2019,15411.0,7.478056629543237,11.457892048194479,10.792314195324462,0.5139764391176864,10.88759069763338,10.051260796825561,13.107756671189508,6.732627782768423,1.975,67.475,1.0367872595421397,0.995669210146422
Sabah,2019,22035.0,8.26985940130081,11.357927476278178,10.582243347089742,0.46038870788280795,9.995823353959505,10.060576767778903,5.993750640303247,7.5650939183032895,5.875,70.725,1.048682687034065,1.047938656517745
Sarawak,2019,19793.0,7.939515260662406,11.82597687707852,10.794686543178672,0.35654659945909,10.79421689539825,9.922652721797139,7.265502494654312,7.1706963001704125,3.225,68.075,0.9881005098620731,0.943924707999775
Terengganu,2019,14158.0,7.126489121807647,10.491288661778372,9.826005517706351,0.5141279348187193,10.272554818952862,9.288134399416203,8.685415829650463,6.1576673079593816,3.625,61.224999999999994,0.9190030266712709,0.9562983932957123
W.P. Kuala Lumpur,2019,22633.0,7.485772152288451,12.362194351608341,12.232377898580078,0.8782566174700017,11.784177478302027,10.727136541160231,25.56858345021038,6.735275136219039,2.625,70.0,1.0328871193808526,1.0032434053881776
W.P. Labuan,2019,524.0,4.598145571051127,8.938960428132718,8.682304328239647,0.7736342209141801,11.248570136063728,7.436617265234227,17.089627391742194,3.717831276063704,4.05,61.925,1.0064311686201222,1.0633870151296425
Johor,2023,15804.89,8.320496810116875,11.909754885968999,11.294573080165357,0.5405426125913173,10.49701335483426,10.347660421747342,7.592520451889365,7.526151973328094,2.45,70.35,1.0397229459882769,1.0510638681037665
Kedah,2023,13444.055,7.69133713701329,10.857018402864757,10.282899881780363,0.5632010999610364,10.073436544833603,9.484481173861296,6.00831315945736,6.948897222313312,2.45,66.55,0.9627990304563179,1.0065461879935529
Kelantan,2023,7549.37,7.528224234044097,10.228256139281159,9.896915805834432,0.717960781388938,9.6077871842192,8.38022733634308,2.3443381008710613,6.662973040845577,3.9749999999999996,61.625,0.8955269440840755,0.9477655618286105
Melaka,2023,15558.661,6.935662232235145,10.755078897001093,10.087596344606556,0.5129984001693286,10.727171943748086,9.810439811486056,17.721482057765243,6.095824562432225,2.75,66.95,0.9586708384663185,0.9989825044796815
Negeri Sembilan,2023,14959.47,7.11061448699364,10.857596591574897,10.221102350030055,0.5291442280090757,10.654737383563393,9.16282938930513,7.785125316352355,6.251663006373203,2.4,67.225,0.9286106235532249,1.0154785380480293
Pahang,2023,16455.567,7.4044008391742935,11.082069869313601,10.430585136947174,0.5212712536215709,10.585424309121445,10.151284691288994,15.59396299902629,6.610830625163423,2.65,65.625,0.9352389881568857,0.9492782985313847
Perak,2023,17107.518,7.840391689392378,11.32284244177051,10.867831643872448,0.6344411172807312,10.390206031360268,9.708080756193517,6.473319691484338,6.99110788750068,3.25,64.975,0.990940508247299,1.0025122234528216
Perlis,2023,1950.771,5.680513847716846,8.75533853108558,8.404754350080628,0.7042765445424266,9.982579962350869,7.126890808898808,4.247697031729785,4.763881877142913,2.175,66.0,0.9887891969285669,1.0728904976723665
Pulau Pinang,2023,13127.587,7.480202674304298,11.661202865093307,10.927529533985,0.48014202611425827,11.088755469771145,10.087224773471245,13.55861446462823,6.8365009236958345,2.125,72.225,1.0364669072356012,0.9749948224785471
Sabah,2023,16080.074,8.187772037381718,11.332253898193763,10.656525721163185,0.5087857995523377,10.052237139794181,10.061345637151708,6.511524452970779,7.622260249494726,7.525,70.675,1.0710623189827784,1.04213151804929
Sarawak,2023,17901.19,7.824965587915676,11.86892159256527,10.909145439374722,0.382978604919598,10.951711283631731,9.959016862328609,8.449026895256363,7.251291790468135,3.45,69.9,0.9904172163049048,0.9374645452335287
Selangor,2023,27579.478,8.883182620536761,12.916042153957502,12.42267848047291,0.6105691808629488,10.940614812402877,10.12523012293471,3.462696089989875,8.240767527220155,2.425,76.7,1.0995526580686892,1.0522884644822028
Terengganu,2023,11760.516,7.098375638590786,10.55150759933163,9.900126109210523,0.5213250736144162,10.360887239722981,9.318207742845189,9.205785123966942,6.21555764745778,4.425,60.225,0.9123304297898472,0.9554733155046509
W.P. Kuala Lumpur,2023,22232.643,7.603748405992001,12.376596595932634,12.29637366861258,0.922910581469601,11.680603468922769,10.761661764674606,23.521463828089942,6.7433227550239225,3.325,73.325,1.0285012410013772,0.9988384343175126
W.P. Labuan,2023,331.36,4.59511985013459,9.002691530229955,8.768788291416262,0.7914383927084602,11.315326959077503,7.436617265234227,17.141414141414142,3.8416005411316,6.75,66.525,0.9500074496422354,1.055097832644498
W.P. Putrajaya,2023,1900.379,4.777441406928545,9.474869138372165,9.438470509577094,0.9642558367181144,11.605183010425758,7.478169694159785,14.890572390572391,3.6454498961866,0.825,75.825,1.2113627030936003,0.9391933871795564
Johor,2024,17138.338,8.339118603469606,11.97255208885017,11.352746806665055,0.5380491951588431,10.541188764362703,10.347660421747342,7.452442405123794,7.64025537549465,2.25,71.52499999999999,1.0302695202307457,1.03917620663867
Kedah,2024,14651.4879543306,7.703955314598164,10.898617301785384,10.319663758146726,0.5604845824439711,10.102417266169356,9.484481173861296,5.932975508547202,6.872283529673884,2.5,66.39999999999999,0.9782601805253759,1.003349868793118
Kelantan,2024,10514.411,7.5432203792009975,10.261127660554125,9.930909461596372,0.7187668821356034,9.625662560335265,8.38022733634308,2.309444356162932,6.547036455286382,3.95,59.275,0.8861873082842341,0.9328300417295413
Melaka,2024,19128.405,6.953397636860839,10.79639094008653,10.133306652710827,0.5152596722792129,10.750748582207828,9.810439811486056,17.409955096971434,6.234900801689954,1.9500000000000002,69.9,0.9358300258144948,0.9927294129100491
Negeri Sembilan,2024,17784.532,7.122463351475245,10.902928724231813,10.265652110931157,0.5287304024141669,10.688220651738705,9.16282938930513,7.693424768051634,6.319958614030018,2.875,67.375,0.9253492704675839,1.0267148717358692
Pahang,2024,20173.876,7.419200710627534,11.138290602903453,10.479167841210982,0.5173049352104868,10.626845171258056,10.151284691288994,15.36487377825748,6.600924365469373,2.1750000000000003,64.75,0.9369569887550229,0.9411848003575553
Perak,2024,21776.217,7.85142768759751,11.369285298998332,10.910441648104621,0.6320140520072873,10.42561289038296,9.708080756193517,6.402272904179964,7.052656168234863,3.325,67.475,0.9925726098700822,0.9978980347731427
Perlis,2024,3225.428,5.693058511293225,8.786416035806873,8.436084866173921,0.7044547570611731,10.001112803495785,7.126890808898808,4.1947439353099725,4.870223140379511,4.0,62.975,0.9945447950160065,1.0804543785041973
Pulau Pinang,2024,16604.803,7.49581968308893,11.707152848629049,10.975471978892186,0.4810996442458614,11.119088444522255,10.087224773471245,13.348514301582894,6.834610944944134,2.225,71.75,1.0481318828381152,1.003066656636236
Sabah,2024,20591.813,8.227375506834035,11.34457798241032,10.697207292261945,0.523420202969223,10.024957754558423,10.061345637151708,6.258685195082843,7.446468406235018,7.55,70.875,1.0701076601784123,1.0244491744808146
Sarawak,2024,19625.552,7.831021624592718,11.906244797532556,10.956205228376932,0.38672572074151745,10.982978451921976,9.959016862328609,8.398013902681232,7.101573000914518,3.275,70.075,0.9914456469295542,0.9407599821222327
Selangor,2024,34460.8280456694,8.904181992276797,12.978331102423825,12.483605900006522,0.6097384389257049,10.981904389129166,10.12523012293471,3.3907398101240034,8.289150157213713,2.375,76.925,1.100873748454828,1.052628784090557
Terengganu,2024,14460.728,7.115988217560592,10.595411585355773,9.940090467243005,0.5192752871109644,10.387178646777317,9.318207742845189,9.045066991473812,6.170917409797458,3.4,60.775,0.9095717893001912,0.9411139973183349
W.P. Kuala Lumpur,2024,26982.957,7.634095426897846,12.4369735347463,12.350517094795078,0.9171755001240818,11.71063338683059,10.761661764674606,22.81837968561064,7.050144202601212,2.9,75.375,1.0320726609355904,1.010784187911266
W.P. Labuan,2024,449.63,4.613138355637268,9.054062865388783,8.830218250285329,0.7994393455188444,11.348679788733653,7.436617265234227,16.835317460317462,3.787026515253461,6.2,67.15,0.9826553359934355,1.058647042424296
W.P. Putrajaya,2024,2556.836,4.789988622980633,9.525332482228922,9.487479866230954,0.9628548398337966,11.643099138230426,7.478169694159785,14.704904405652536,4.09016919081162,1.725,78.8,1.1851705764063265,0.9542125595741198
Johor,2025,18196.973,8.343815518583586,12.04911170060441,11.446868265891533,0.547581793070864,10.61305146100296,10.347660421747342,7.417520991413143,7.666097015441784,2.4,71.76666666666667,1.0348316071955581,1.0407015887172222
Kedah,2025,15607.884,7.708455569706803,10.938504643885704,10.358021770031874,0.5596280715478353,10.137804353161037,9.484481173861296,5.906335593372548,6.888130635845837,2.466666666666667,66.3,0.9760262455302297,1.0130017749565003
Kelantan,2025,12062.016,7.553234165840581,10.30144998583558,9.969900659289664,0.7178107482186351,9.655971098977135,8.38022733634308,2.2864334784204727,6.570369291684567,4.3999999999999995,59.666666666666664,0.876809356147178,0.9278738119595344
Melaka,2025,20832.201530282,6.9584483932976555,10.825482206075694,10.179980193641706,0.5243992210875505,10.774789091760177,9.810439811486056,17.322243346007603,6.251068595424966,2.1666666666666665,69.2,0.9382502522288798,0.9819444080126607
Negeri Sembilan,2025,19356.545,7.126006884215919,10.928942793701399,10.295088191536626,0.5305428230322323,10.710691188467617,9.16282938930513,7.666211110217863,6.3372386252449715,2.9,67.26666666666667,0.9444547395007584,1.0347559216221178
Pahang,2025,23161.166,7.424642494126723,11.1699037049692,10.527831691804517,0.5262009983135124,10.653016489824614,10.151284691288994,15.28148854961832,6.645524338959881,1.8,66.06666666666666,0.9364383223176231,0.9415838207905988
Perak,2025,23642.055,7.853138685059564,11.424415281695042,10.94376308044499,0.6183799520807411,10.479031875617615,9.708080756193517,6.391327997513404,7.06726301271041,3.4333333333333336,67.46666666666667,0.9858545926246217,0.9880999221817099
Perlis,2025,3755.682,5.6937321388027,8.806210621880512,8.467000554241139,0.7123327953022773,10.020233762059949,7.126890808898808,4.191919191919192,4.892101977049168,3.266666666666667,63.23333333333333,0.9758066176621986,1.0830207486294363
Pulau Pinang,2025,17717.979,7.497927983914253,11.777467241551863,11.016007266415611,0.46698414383384346,11.187294536619747,10.087224773471245,13.320401263647952,6.834610944944134,2.566666666666667,71.2,1.0587710448109484,1.0051674841958922
Sabah,2025,22361.168,8.230710399539939,11.393848575145421,10.740892099373218,0.5205046403588152,10.07089345458762,10.061345637151708,6.237847915834332,7.500861105361856,6.2,70.43333333333334,1.0908367135434898,1.0223049952347227
Sarawak,2025,22721.527,7.835539704567506,11.94152908111265,11.00859001770442,0.3933957944265737,11.01374465552728,9.959016862328609,8.360156589821662,7.103486522686009,3.3000000000000003,69.63333333333334,0.9935964749727181,0.9390656559032604
Selangor,2025,36376.442,8.91041026430249,13.039228798820332,12.542126744744124,0.608290902077306,11.03657381349998,10.12523012293471,3.369686989620311,8.318294998217482,1.9666666666666668,78.03333333333335,1.1109326634683359,1.0449684792207679
Terengganu,2025,15462.278,7.127533172820045,10.611439918464558,9.975765841125009,0.5295783911825354,10.39166202462665,9.318207742845189,8.941242575052176,6.192566967545312,2.8666666666666667,60.699999999999996,0.9194720695122202,0.9394154010265019
W.P. Kuala Lumpur,2025,35059.9331815272,7.63781281356218,12.487877412911194,12.401578584295512,0.9173200687721091,11.757819878331153,10.761661764674606,22.733712413261376,7.0927953594620385,2.966666666666667,75.5,1.0313175613070604,1.0276211211079924
W.P. Labuan,2025,604.37,4.6141299273595635,9.071104856014323,8.85092610809558,0.802375362217394,11.364730207636896,7.436617265234227,16.818632309217044,3.799973501619523,4.8,66.26666666666667,0.9875567086018628,1.0458778165411955
W.P. Putrajaya,2025,3146.484,4.793308128103486,9.572613596260153,9.536123324070916,0.9641674730894254,11.687060747138805,7.478169694159785,14.656172328086164,4.107041393016508,1.5333333333333332,77.66666666666667,1.1390450305763173,0.9645970498998855"""
    df = pd.read_csv(io.StringIO(csv_data))
    df['visitors_M'] = df['visitors_000'] / 1000
    return df

df = load_data()


# --- 4. Sidebar Navigation & Global Filters ---
with st.sidebar:
    st.markdown("<h2 style='color:#E27D60; margin-bottom:0; font-size: 1.8rem;'>🎯 LestariLens</h2>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 0.75rem; color: #737373; font-weight:bold; letter-spacing: 1px; margin-top: -5px; margin-bottom: 25px;'>MALAYSIA TOURISM<br>INTELLIGENCE</p>", unsafe_allow_html=True)
    
    selected_page = st.radio("Navigation", ["Overview", "Visitor flows", "Sustainability", "Scenario lab", "Evidence"], label_visibility="collapsed")
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 0.85rem; color: #2D3142; font-weight:bold; margin-bottom: -5px;'>📅 Global Year Filter</p>", unsafe_allow_html=True)
    
    # --- 1. FIXED: Show all unique years from the dataset ---
    available_years = sorted(df['year'].unique().tolist(), reverse=True)
    selected_year = st.selectbox("Year", available_years, label_visibility="collapsed")
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div style="background-color: #DDE2DA; padding: 15px; border-radius: 8px; font-size: 0.8rem; color: #555;">
        <b>DOSM official data first</b><br><br>Every insight shows its source, year and analytical limitation.
    </div>
    """, unsafe_allow_html=True)


# ==========================================
# PAGE 1: OVERVIEW DASHBOARD
# ==========================================
def render_overview():
    col_head1, col_head2 = st.columns([2.5, 1.5])
    states_list = ["Malaysia"] + sorted(df['state'].unique().tolist())

    with col_head1:
        st.markdown(f'<p class="sub-header">NATIONAL PULSE · {selected_year} OVERVIEW</p>', unsafe_allow_html=True)
        st.markdown('<h1>Grow tourism value.<br>Protect what makes Malaysia special.</h1>', unsafe_allow_html=True)

    with col_head2:
        st.markdown("<br>", unsafe_allow_html=True)
        selected_region = st.selectbox("Region", states_list, label_visibility="collapsed")
            
        if st.button("✨ Generate brief", type="primary", use_container_width=True):
            st.toast(f"✅ Generating official brief for {selected_region} ({selected_year})...")

    # --- 2. FIXED: Safely look back exactly 1 available year in the dataset to calculate growth ---
    all_years_sorted = sorted(df['year'].unique().tolist())
    curr_idx = all_years_sorted.index(selected_year)
    prev_year = all_years_sorted[curr_idx - 1] if curr_idx > 0 else None

    # Filtering Logic based on Global Year & State
    if selected_region == "Malaysia":
        df_current = df[df['year'] == selected_year]
        df_prev = df[df['year'] == prev_year] if prev_year else pd.DataFrame()
        
        chart_data = df_current.sort_values(by='visitors_M', ascending=False).head(4).copy()
        chart_title = f"Where visitors concentrate (Top Destinations, {selected_year})"
        y_axis = 'state'
    else:
        df_current = df[(df['year'] == selected_year) & (df['state'] == selected_region)]
        df_prev = df[(df['year'] == prev_year) & (df['state'] == selected_region)] if prev_year else pd.DataFrame()
        
        chart_data = df[(df['state'] == selected_region) & (df['year'] <= selected_year)].sort_values(by='year', ascending=True).tail(5).copy()
        chart_data['year'] = chart_data['year'].astype(str)
        chart_title = f"Historical Visitor Trend ({selected_region})"
        y_axis = 'year'

    v_current = df_current['visitors_M'].sum() if not df_current.empty else 0
    v_prev = df_prev['visitors_M'].sum() if not df_prev.empty else 0
    v_growth = ((v_current - v_prev) / v_prev) * 100 if v_prev > 0 else 0

    # Handle the oldest year where prev_year is None
    if prev_year:
        delta_label = f"↑ {v_growth:.1f}% vs {prev_year}" if v_growth >= 0 else f"↓ {abs(v_growth):.1f}% vs {prev_year}"
    else:
        delta_label = "N/A (Baseline year)"

    # Main KPI Row
    st.markdown("<br>", unsafe_allow_html=True)
    k1, k2, k3, k4 = st.columns(4)
    with k1.container(border=True): st.metric(f"Domestic visitors ({selected_year})", f"{v_current:.1f}M", delta_label)
    with k2.container(border=True): st.metric("Tourism expenditure", "RM121.3B", "↑ 13.6% vs last year")
    with k3.container(border=True): st.metric("Domestic trips", "332.2M", "1.15 trips per visitor", delta_color="off")
    with k4.container(border=True): st.metric("Average length of stay", "2.56", f"Nights · {selected_year}", delta_color="off")

    st.markdown("<br>", unsafe_allow_html=True)
    mid_col1, mid_col2 = st.columns([2.3, 1])

    with mid_col1:
        with st.container(border=True):
            st.subheader("Visitor Volume")
            st.caption(chart_title)
            
            if selected_region == "Malaysia":
                colors = ['#E5E2D9', '#E8B87B', '#E27D60', '#85A88F']
                chart_data['Color'] = colors[-len(chart_data):]
                fig_bar = px.bar(chart_data.iloc[::-1], x='visitors_M', y='state', orientation='h', text='visitors_M')
                fig_bar.update_traces(marker_color=chart_data.iloc[::-1]['Color'], marker_line_width=0, texttemplate='%{text:.1f}M', textposition='outside', textfont=dict(color='#2D3142', size=11))
            else:
                fig_bar = px.bar(chart_data, x='year', y='visitors_M', orientation='v', text='visitors_M')
                fig_bar.update_traces(marker_color='#E8B87B', marker_line_width=0, texttemplate='%{text:.1f}M', textposition='outside', textfont=dict(color='#2D3142', size=11))
                fig_bar.update_xaxes(type='category')

            fig_bar.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=0, r=40, t=10, b=0), height=280, xaxis=dict(showgrid=False, title=""), yaxis=dict(showgrid=False, showticklabels=False, title=""))
            st.plotly_chart(fig_bar, use_container_width=True)

    with mid_col2:
        # --- 3. FIXED: AI Copilot text handles oldest year cleanly ---
        if selected_region == "Malaysia":
            copilot_title = "Policy copilot"
            copilot_body = "Tourism demand is concentrated in <b>Selangor</b> and <b>W.P. Kuala Lumpur</b>. Compare infrastructure capacities before recommending further mass promotion."
            
            if not chart_data.empty:
                copilot_evi = f"Evidence: {chart_data.iloc[0]['state']} recorded {chart_data.iloc[0]['visitors_M']:.1f}M domestic visitors in {selected_year}."
            else:
                copilot_evi = f"Evidence: Data unavailable for {selected_year}."
        else:
            copilot_title = f"{selected_region} Insights"
            copilot_body = f"In <b>{selected_region}</b>, visitor volumes reached <b>{v_current:.1f}M</b>. Monitor local room capacities and infrastructure strain to sustain this volume."
            
            if prev_year:
                copilot_evi = f"Evidence: {selected_region} grew by {v_growth:.1f}% compared to {prev_year}."
            else:
                copilot_evi = f"Evidence: {selected_region} recorded {v_current:.1f}M visitors in {selected_year} (Baseline)."

        st.markdown(f"""
        <div style="background-color: #3B3C54; padding: 25px; border-radius: 12px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); margin-bottom: 10px; height: 320px;">
            <div style="color: white; font-family: sans-serif; font-size: 1.4rem; font-weight: 600; margin-bottom: 15px; display: flex; align-items: center;">
                <span style="margin-right: 8px; font-size: 1.6rem;">🎯</span> {copilot_title}
            </div>
            <div style="color: #F3F4F6; font-family: sans-serif; font-size: 0.95rem; line-height: 1.5; margin-bottom: 20px;">
                {copilot_body}
            </div>
            <div style="background-color: rgba(255,255,255,0.08); padding: 15px; border-radius: 8px; font-family: sans-serif; font-size: 0.85rem; color: #D1D5DB;">
                {copilot_evi}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        with st.expander("💬 Ask why · show sources"):
            source_years = f"{prev_year}-{selected_year}" if prev_year else f"{selected_year}"
            st.write(f"**Source:** DOSM Domestic Tourism Survey (States), {source_years}. Analyzed by LestariLens ML model.")

    # Bottom Row
    st.markdown("<br>", unsafe_allow_html=True)
    bot_col1, bot_col2 = st.columns([1.5, 1.5])

    with bot_col1:
        with st.container(border=True):
            st.subheader("What visitors spend on")
            st.caption(f"Share of domestic tourism expenditure, {selected_year}")
            
            pie_data = pd.DataFrame({
                'Category': ['Shopping', 'Food & beverages', 'Automotive fuel', 'Other categories'],
                'Value': [36.9, 16.1, 13.5, 33.5],
                'Color': ['#E27D60', '#85A88F', '#E8B87B', '#E4E4E4']
            })
            
            fig_pie = go.Figure(data=[go.Pie(
                labels=pie_data['Category'], values=pie_data['Value'], hole=0.6,
                marker=dict(colors=pie_data['Color']), textinfo='none', sort=False, direction='clockwise'
            )])
            fig_pie.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=0, r=0, t=10, b=0), 
                height=250, showlegend=True, 
                annotations=[dict(text=str(selected_year), x=0.5, y=0.5, font_size=20, font_color="#2D3142", showarrow=False)]
            )
            st.plotly_chart(fig_pie, use_container_width=True)

    with bot_col2:
        with st.container(border=True):
            st.subheader("Scenario lab")
            st.caption("Explore redistribution based on selected region")
            
            shift_pct = st.slider("Shift projected demand", min_value=0, max_value=20, value=5, format="%d%%")
            
            if selected_region == "Malaysia":
                target_state = "Pahang"
                base_vol = df[(df['year'] == selected_year) & (df['state'] == 'Pahang')]['visitors_M'].sum()
                scenario_calc = base_vol + (v_current * (shift_pct / 100))
            else:
                target_state = selected_region
                scenario_calc = v_current * (1 + (shift_pct / 100))
                
            c1, c2 = st.columns(2)
            c1.metric("Projected Shift Scenario", f"{scenario_calc:.1f}M")
            c2.metric("Target State", target_state)


# ==========================================
# PAGE 2: VISITOR FLOWS
# ==========================================
def render_visitor_flows():
    st.markdown(f'<p class="sub-header">ANALYTICS · HISTORICAL TRENDS ({selected_year})</p>', unsafe_allow_html=True)
    st.header("Visitor Flows & Growth Trajectories")
    st.markdown("Track the movement and long-term growth of domestic visitors across all states up to the selected year.")
    
    df_trend = df[df['year'] <= selected_year].groupby(['year', 'state'])['visitors_M'].sum().reset_index()
    
    top_3 = df[df['year'] == selected_year].sort_values('visitors_M', ascending=False).head(3)['state'].tolist()
    df_trend['Highlight'] = df_trend['state'].apply(lambda x: x if x in top_3 else 'Other States')
    
    fig_line = px.line(df_trend, x="year", y="visitors_M", color="Highlight", line_group="state", hover_name="state",
                       color_discrete_map={'Selangor': '#E27D60', 'W.P. Kuala Lumpur': '#85A88F', 'Perak': '#E8B87B', 'Other States': '#DEDAD0'})
    
    fig_line.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=500,
                           xaxis=dict(showgrid=False, title="Year"), yaxis=dict(showgrid=True, gridcolor='#E5E2D9', title="Visitors (Millions)"))
    st.plotly_chart(fig_line, use_container_width=True)


# ==========================================
# PAGE 3: SUSTAINABILITY
# ==========================================
def render_sustainability():
    st.markdown(f'<p class="sub-header">INFRASTRUCTURE · CAPACITY ({selected_year})</p>', unsafe_allow_html=True)
    st.header("Sustainability & Tourism Strain")
    st.markdown(f"Analyze local infrastructure capacity versus economic output based on the **{selected_year}** global filter.")
    
    df_yr = df[df['year'] == selected_year].copy()
    
    fig_scatter = px.scatter(df_yr, x="log_gdp_per_capita", y="rooms_per_1k_residents", 
                             size="visitors_M", color="visitors_M", hover_name="state",
                             color_continuous_scale=["#85A88F", "#E8B87B", "#E27D60"],
                             labels={"log_gdp_per_capita": "Economic Strength (Log GDP per Capita)", 
                                     "rooms_per_1k_residents": "Infrastructure Capacity (Rooms per 1k Residents)"})
    
    fig_scatter.add_vline(x=df_yr['log_gdp_per_capita'].median(), line_width=1, line_dash="dash", line_color="gray")
    fig_scatter.add_hline(y=df_yr['rooms_per_1k_residents'].median(), line_width=1, line_dash="dash", line_color="gray")
    
    fig_scatter.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=500)
    st.plotly_chart(fig_scatter, use_container_width=True)


# ==========================================
# PAGE 4: SCENARIO LAB
# ==========================================
def render_scenario_lab():
    st.markdown(f'<p class="sub-header">POLICY · SIMULATION ({selected_year})</p>', unsafe_allow_html=True)
    st.header("Scenario Lab: Demand Redistribution")
    st.markdown(f"Simulate the impact of shifting tourism volume from high-density states to developing targets using the **{selected_year}** baseline.")
    
    col1, col2, col3 = st.columns([1, 1, 1.5])
    df_yr = df[df['year'] == selected_year]
    
    with col1:
        source_state = st.selectbox("Source State (Reduce Demand)", df_yr.sort_values('visitors_M', ascending=False)['state'])
    with col2:
        target_state = st.selectbox("Target State (Increase Demand)", df_yr.sort_values('visitors_M')['state'], index=1)
    with col3:
        shift_pct = st.slider("Percentage of Source Visitors to Shift", min_value=0, max_value=30, value=5, format="%d%%")
        
    source_vol = df_yr[df_yr['state'] == source_state]['visitors_M'].values[0]
    target_vol = df_yr[df_yr['state'] == target_state]['visitors_M'].values[0]
    
    shift_amount = source_vol * (shift_pct / 100)
    
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    
    with c1.container(border=True):
        st.subheader(f"📉 {source_state} (Source)")
        st.metric("New Projected Visitors", f"{source_vol - shift_amount:.1f}M", f"-{shift_amount:.1f}M shifted", delta_color="inverse")
        
    with c2.container(border=True):
        st.subheader(f"📈 {target_state} (Target)")
        st.metric("New Projected Visitors", f"{target_vol + shift_amount:.1f}M", f"+{shift_amount:.1f}M gained")


# ==========================================
# PAGE 5: EVIDENCE
# ==========================================
def render_evidence():
    st.markdown('<p class="sub-header">DATA · TRANSPARENCY</p>', unsafe_allow_html=True)
    st.header("Evidence & Raw Data")
    st.markdown("Direct access to the underlying DOSM (Department of Statistics Malaysia) dataset.")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Records", len(df))
    col2.metric("Total States", df['state'].nunique())
    col3.metric("Year Range", f"{df['year'].min()} - {df['year'].max()}")
    
    st.dataframe(df, use_container_width=True, height=500)


# --- 9. Execution Engine ---
if selected_page == "Overview":
    render_overview()
elif selected_page == "Visitor flows":
    render_visitor_flows()
elif selected_page == "Sustainability":
    render_sustainability()
elif selected_page == "Scenario lab":
    render_scenario_lab()
elif selected_page == "Evidence":
    render_evidence()