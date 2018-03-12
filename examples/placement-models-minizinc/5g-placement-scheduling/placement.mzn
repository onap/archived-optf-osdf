include "globals.mzn";

int: NCR;  % number of cloud regions
int: N_ATTR; %  number of capability related attributes
array[1..N_ATTR] of float: w_attr; % weights of each attribute

int: N_UTILIZATION_METRICS; % number of dynamic capacity metrics of interest
% set of 1..N_UTILIZATION_METRICS: U_METRICS;
array[1..N_UTILIZATION_METRICS] of float: w_metrics; % weights of each capacity metric

int: cust_type;  % customer type, 0 = regular, 1 = silver, 2 = gold
int: N_VMS; % number of VMs in VNF
int: N_CAPM; % number of metrics for cloud region capacity check
int: MIN_GUAR_ADDL_WT; % additional weight for min guarantee capability

float: C_ALLOC_THRESHOLD; % allocation threshold for cloud
float: CUST_ALLOC_THRESHOLD; % allocation threshold for customer in cloud
float: AVG_CPU_UTILIZATION_THRESHOLD;
float: PEAK_CPU_UTILIZATION_THRESHOLD;

int: u_lat;
int: u_lon;
float: dist_norm;
float: max_dist_ue;
array[1..NCR] of int: cr_lat;
array[1..NCR] of int: cr_lon;

enum CUST_TYPES = { STANDARD, SILVER, GOLD };
enum ATTRIBUTES = { CORE_DC, DIRECT_CONN, MIN_GUARANTEE, SRIOV };
enum METRICS = { AVG_CPU_UTILIZATION, PEAK_CPU_UTILIZATION };
enum CLOUD_REGION_CAPACITY = {CPU_CLOUD, MEMORY_CLOUD};
enum WL_TYPES = { W1, W2, W3, W4, W5 };
int: N_WL;

% set of 1..N_CAPM: CAP_METRICS;

% whether a cloud region has the corresponding capability -- data will be customer specific
array[1..NCR, 1..N_ATTR] of int: capabilities;
array[1..NCR, 1..N_UTILIZATION_METRICS] of float: cpu_utilization;  % how much capacity is already dynamically utilized     (fraction)
array[1..NCR, 1..N_CAPM] of int: c_alloc_capacity; % how much percent is already allocated in the cloud
array[1..NCR, 1..N_CAPM] of int: c_total_capacity;  % total cloud capacity
array[1..NCR, 1..N_CAPM] of float: c_alloc_capacity_norm;
array[1..NCR, 1..N_CAPM] of int: cust_alloc_capacity; % how much percent is already allocated in the cloud for the customer
array[1..NCR, 1..N_CAPM] of int: cust_total_capacity; % total cloud capacity for customer
array[1..NCR, 1..N_CAPM] of float: cust_alloc_capacity_norm;

% VM requirements for each type of capacity (vm cpu, memory, etc.)
% TODO: establish a standard for units (MB RAM, GB disk, N virtual cores, etc.)
array[1..N_VMS, 1..N_CAPM] of int: vm_reqs;
array[1..N_CAPM] of int: vm_reqs_sums = [ sum(k in 1..N_VMS) (vm_reqs[k,j]) | j in 1..N_CAPM ];
array[1..NCR, 1..N_CAPM] of float: vm_reqs_sums_norm;
%forall(i in 1..NCR, j in 1..N_CAPM) (
%  vm_reqs_sums_norm[i, j] = vm_reqs_sums[j]/c_total_capacity[i, j]
%)
%array[1..NCR, 1..N_CAPM] of float: vm_reqs_sums_norm = [ ((vm_reqs_sums[j]/c_total_capacity[i,j]) | j in 1..N_CAPM) | i in 1..NCR ];

array[1..N_WL] of var int: s_regions;  % target cloud regions (solution to the problem)

function var float: dist(var int: x1, var int: y1, var int: x2, var int: y2) = (sqrt(pow((x1-x2),2) + pow((y1-y2),2)))/dist_norm;

% custom constraints
constraint forall (s in s_regions) (
    cpu_utilization[s, AVG_CPU_UTILIZATION] <= AVG_CPU_UTILIZATION_THRESHOLD /\    % hard constraint: need some capacity available
    cpu_utilization[s, PEAK_CPU_UTILIZATION] <= PEAK_CPU_UTILIZATION_THRESHOLD /\  % hard constraint: need some capacity available
    cust_alloc_capacity[s, CPU_CLOUD] <= (CUST_ALLOC_THRESHOLD*(cust_total_capacity[s, CPU_CLOUD])) - (vm_reqs_sums[CPU_CLOUD]) /\
    cust_alloc_capacity[s, MEMORY_CLOUD] <= (CUST_ALLOC_THRESHOLD*(cust_total_capacity[s, MEMORY_CLOUD])) - (vm_reqs_sums[MEMORY_CLOUD]) /\
    c_alloc_capacity[s, CPU_CLOUD] <= (C_ALLOC_THRESHOLD*(c_total_capacity[s, CPU_CLOUD])) - (vm_reqs_sums[CPU_CLOUD]) /\
    c_alloc_capacity[s, MEMORY_CLOUD] <= (C_ALLOC_THRESHOLD*(c_total_capacity[s, MEMORY_CLOUD])) - (vm_reqs_sums[MEMORY_CLOUD])
);

% specific constraints based on the workload
constraint [capabilities[s_regions[x], CORE_DC] | x in WL_TYPES] = [1, 1, 0, 0, 0];

constraint forall (x in [W3, W4, W5])
(dist(u_lat, u_lon, cr_lat[s_regions[x]], cr_lon[s_regions[x]]) < max_dist_ue/dist_norm);

constraint all_different([s_regions[x] | x in WL_TYPES]);

% custom soft constraint for gold customers -- give a large weight to Minimum Guarantee
var float: additional_obj = sum(s in s_regions) (bool2int(cust_type = GOLD) * capabilities[s, MIN_GUARANTEE] * MIN_GUAR_ADDL_WT);

% TODO: global constraints (such as data validation)

% Objective for utilization
var float: obj_c_capacity = sum(k in 1..N_CAPM, s in s_regions) (
		  (1 - c_alloc_capacity_norm[s, k] - vm_reqs_sums_norm[s, k]) +
%                  (1 - cust_alloc_capacity_norm[s, k] - vm_reqs_sums_norm[s, k]));
                  (1 - cust_alloc_capacity_norm[s, k] - vm_reqs_sums_norm[s, k]) +
                  (1 - dist(u_lat, u_lon,cr_lat[s], cr_lon[s])));

% Objective for utilization
var float: obj_utilization = sum(k in 1..N_UTILIZATION_METRICS, s in s_regions) ( w_metrics[k] * (1 - cpu_utilization[s, k]) );

% Objective for capabilities
var float: obj_capabilities = sum(k in 1..N_ATTR, s in s_regions) ( w_attr[k] * capabilities[s, k] );

% Overall objective function
var float: obj = obj_c_capacity + obj_utilization + obj_capabilities + additional_obj;

solve maximize obj;

output [ "Solution: \n"
         ++ concat(["Cloud Region for W" ++ format(x) ++ " = " ++ format(s_regions[x]) ++ "\n" | x in 1..N_WL]) ]
         ++ [ "Objective function value: ", show(obj), "\n", "Customer type: ", show(cust_type), "\n"];
