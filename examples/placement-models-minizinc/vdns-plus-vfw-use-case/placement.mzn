int: N_CLOUD_REGIONS;  % number of cloud regions
% set of 1..N_CLOUD_REGIONS: C_REGIONS;

int: N_ATTRIBUTES; %  number of capability related attributes
% set of 1..N_ATTRIBUTES: ATTRIBS;
array[1..N_ATTRIBUTES] of float: w_attributes; % weights of each attribute

int: N_UTILIZATION_METRICS; % number of dynamic capacity metrics of interest
% set of 1..N_UTILIZATION_METRICS: U_METRICS;
array[1..N_UTILIZATION_METRICS] of float: w_metrics; % weights of each capacity metric

int: cust_type;  % customer type, 0 = regular, 1 = silver, 2 = gold
int: N_VMS; % number of VMs in VNF
int: N_CAPACITY_METRICS; % number of metrics for cloud region capacity check

float: C_ALLOC_THRESHOLD; % allocation threshold for cloud
float: CUST_ALLOC_THRESHOLD; % allocation threshold for customer in cloud
float: AVG_CPU_UTILIZATION_THRESHOLD;
float: PEAK_CPU_UTILIZATION_THRESHOLD;

enum CUST_TYPES = { STANDARD, SILVER, GOLD };
enum ATTRIBUTES = { CORE_DC, DIRECT_CONN, MIN_GUARANTEE, SRIOV };
enum METRICS = { AVG_CPU_UTILIZATION, PEAK_CPU_UTILIZATION };
enum CLOUD_REGION_CAPACITY = {CPU_CLOUD, MEMORY_CLOUD};
enum VNFS_TYPES = { VDNS, VFW };
int: N_VNFS;

% set of 1..N_CAPACITY_METRICS: CAP_METRICS;

% whether a cloud region has the corresponding capability -- data will be customer specific
% array[1..N_CLOUD_REGIONS, 1..N_CLOUD_REGIONS] of float: c_dist;
array[1..N_CLOUD_REGIONS, 1..N_ATTRIBUTES] of int: capabilities;
array[1..N_CLOUD_REGIONS, 1..N_UTILIZATION_METRICS] of float: cpu_utilization;  % how much capacity is already dynamically utilized     (fraction)
array[1..N_CLOUD_REGIONS, 1..N_CAPACITY_METRICS] of int: c_alloc_capacity; % how much percent is already allocated in the cloud
array[1..N_CLOUD_REGIONS, 1..N_CAPACITY_METRICS] of int: c_total_capacity;  % total cloud capacity
array[1..N_CLOUD_REGIONS, 1..N_CAPACITY_METRICS] of float: c_alloc_capacity_norm;
array[1..N_CLOUD_REGIONS, 1..N_CAPACITY_METRICS] of int: cust_alloc_capacity; % how much percent is already allocated in the cloud for the customer
array[1..N_CLOUD_REGIONS, 1..N_CAPACITY_METRICS] of int: cust_total_capacity; % total cloud capacity for customer
array[1..N_CLOUD_REGIONS, 1..N_CAPACITY_METRICS] of float: cust_alloc_capacity_norm;

% VM requirements for each type of capacity (vm cpu, memory, etc.)
% TODO: establish a standard for units (MB RAM, GB disk, N virtual cores, etc.)
array[1..N_VMS, 1..N_CAPACITY_METRICS] of int: vm_reqs;
array[1..N_CAPACITY_METRICS] of int: vm_reqs_sums = [ sum(k in 1..N_VMS) (vm_reqs[k,j]) | j in 1..N_CAPACITY_METRICS ];
array[1..N_CLOUD_REGIONS, 1..N_CAPACITY_METRICS] of float: vm_reqs_sums_norm;
%forall(i in 1..N_CLOUD_REGIONS, j in 1..N_CAPACITY_METRICS) (
%  vm_reqs_sums_norm[i, j] = vm_reqs_sums[j]/c_total_capacity[i, j]
%)
%array[1..N_CLOUD_REGIONS, 1..N_CAPACITY_METRICS] of float: vm_reqs_sums_norm = [ ((vm_reqs_sums[j]/c_total_capacity[i,j]) | j in 1..N_CAPACITY_METRICS) | i in 1..N_CLOUD_REGIONS ];

array[1..N_VNFS] of var int: s_regions;  % target cloud regions (solution to the problem)

% custom constraints
constraint forall (s in s_regions) (
    cpu_utilization[s, AVG_CPU_UTILIZATION] <= AVG_CPU_UTILIZATION_THRESHOLD /\    % hard constraint: need some capacity available
    cpu_utilization[s, PEAK_CPU_UTILIZATION] <= PEAK_CPU_UTILIZATION_THRESHOLD /\  % hard constraint: need some capacity available
    cust_alloc_capacity[s, CPU_CLOUD] <= (CUST_ALLOC_THRESHOLD*(cust_total_capacity[s, CPU_CLOUD])) - (vm_reqs_sums[CPU_CLOUD]) /\
    cust_alloc_capacity[s, MEMORY_CLOUD] <= (CUST_ALLOC_THRESHOLD*(cust_total_capacity[s, MEMORY_CLOUD])) - (vm_reqs_sums[MEMORY_CLOUD]) /\
    c_alloc_capacity[s, CPU_CLOUD] <= (C_ALLOC_THRESHOLD*(c_total_capacity[s, CPU_CLOUD])) - (vm_reqs_sums[CPU_CLOUD]) /\
    c_alloc_capacity[s, MEMORY_CLOUD] <= (C_ALLOC_THRESHOLD*(c_total_capacity[s, MEMORY_CLOUD])) - (vm_reqs_sums[MEMORY_CLOUD])
);

% specific constraints based on the VNF
constraint capabilities[s_regions[VDNS], CORE_DC] = 1;  % hard constraint for vDNS: has to be placed in CORE DC

% custom soft constraint for gold customers -- give a large weight to direct connection
var float: additional_obj = sum(s in s_regions) (bool2int(cust_type = GOLD) * capabilities[s, MIN_GUARANTEE] * 1000);

% TODO: global constraints (such as data validation)

% Objective for utilization
var float: obj_c_capacity = sum(k in 1..N_CAPACITY_METRICS, s in s_regions) (
		  (1 - c_alloc_capacity_norm[s, k] - vm_reqs_sums_norm[s, k]) +
                  (1 - cust_alloc_capacity_norm[s, k] - vm_reqs_sums_norm[s, k]));

% Objective for utilization
var float: obj_utilization = sum(k in 1..N_UTILIZATION_METRICS, s in s_regions) ( w_metrics[k] * (1 - cpu_utilization[s, k]) );

% Objective for capabilities
var float: obj_capabilities = sum(k in 1..N_ATTRIBUTES, s in s_regions) ( w_attributes[k] * capabilities[s, k] );

% Overall objective function
var float: obj = obj_c_capacity + obj_utilization + obj_capabilities + additional_obj;

solve maximize obj;

output [ "Solution: \nCloud Region for vDNS = ", show(s_regions[VDNS]) ] 
++ [ if N_VNFS = 2 then "\nCloud Region for vFW = " ++ show(s_regions[VFW]) ++ "\n" else "\n" endif ]
++ [ "Objective function value: ", show(obj), "\n", "Customer type: ", show(cust_type), "\n"];
