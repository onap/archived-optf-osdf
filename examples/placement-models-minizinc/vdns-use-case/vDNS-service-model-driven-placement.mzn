int: N_CLOUD_REGIONS;  % number of cloud regions 

int: N_ATTRIBUTES; %  number of capability related attributes
array[1..N_ATTRIBUTES] of float: W_ATTRIBUTES; % weights of each attribute

int: N_METRICS; % number of dynamic capacity metrics of interest
array[1..N_METRICS] of float: W_METRICS; % weights of each capacity metric

int: CUST_TYPE;  % customer type, 0 = regular, 1 = silver, 2 = gold

enum CUST_TYPES = { STANDARD, SILVER, GOLD };
enum ATTRIBUTES = { CORE_DC, DIRECT_CONN, MIN_GUARANTEE, SRIOV };
enum METRICS = { AVG_UTILIZATION, PEAK_UTILIZATION };
 
% whether a cloud region has the corresponding capability -- data will be customer specific
array[1..N_CLOUD_REGIONS, 1..N_ATTRIBUTES] of int: capabilities; 
array[1..N_CLOUD_REGIONS, 1..N_METRICS] of float: utilization;  % how much capacity is already utilized (fraction)

var int: s;  % target cloud region (solution to the problem)

% custom constraints
constraint capabilities[s, CORE_DC] = 1;   % hard constraint: has to be placed in CORE DC
constraint utilization[s, AVG_UTILIZATION] <= 0.85;   % hard constraint: need some capacity available
% custom soft constraint for gold customers -- give a large weight to direct connection
var float: additional_obj = bool2int(CUST_TYPE = GOLD) * capabilities[s, DIRECT_CONN] * 1000;

% TODO: global constraints (such as data validation)

% Objective for utilization
var float: obj_utilization = sum(k in 1..N_METRICS) ( W_METRICS[k] * (1 - utilization[s, k]) );

% Objective for capabilities
var float: obj_capabilities = sum(k in 1..N_ATTRIBUTES) ( W_ATTRIBUTES[k] * capabilities[s, k] );

% Overall objective function
var float: obj = obj_utilization + obj_capabilities + additional_obj;  % can later add weights to each...

solve maximize obj;

output ["Cloud Region: ", show(s), "\n", "Objective function value: ", show(obj), "\n", "Customer type: ", show(CUST_TYPE), "\n"];
