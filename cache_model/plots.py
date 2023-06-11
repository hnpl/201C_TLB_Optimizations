#import matplotlib.pyplot as plt

import re
import os
import matplotlib.pyplot as plt
import numpy as np


eps = 0.000000001

def extract_variables(filename: str) -> [int, int, str, int, str]:

    print('extracting file: {}'.format(filename))
    stream_class = None
    info = filename.split('_')
    design_class, page_size_bytes, workload_class = info[1], info[2], info[3]
    if (workload_class == 'gemm') or (workload_class == 'gups'):
        num_lanes = info[4]
    elif (workload_class == 'npb') or (workload_class == 'permutating') or (workload_class == 'stream'):
        num_lanes = info[5]
        if (workload_class == 'stream'):
            stream_class = info[4]
    else:
        raise NotImplementedError
    design_class, page_size_bytes, num_lanes = int(design_class), int(page_size_bytes), int(num_lanes)

    return design_class, page_size_bytes, workload_class, num_lanes, stream_class


def extract_design_1(lines, num_lanes):

    mem_access_num = re.findall(r'\d+', lines[0])[0]
    print('mem_access_num: {}'.format(mem_access_num))
    ptw_pool_missrate = float(re.findall(r'\d+', lines[1])[0]) / (float(re.findall(r'\d+', lines[2])[0])+eps)
    print('ptw_pool_missrate: {}'.format(ptw_pool_missrate))
    l2_tlb_missrate = float(re.findall(r'\d+', lines[4])[1]) / (float(re.findall(r'\d+', lines[3])[1])+eps)
    print('l2_tlb_missrate: {}'.format(l2_tlb_missrate))
    l1_tlb_access_num, l1_tlb_miss_num = eps, eps
    for i in range(5, 4+num_lanes*3, 3):
        # print('i: {}'.format(i))
        l1_tlb_access_num = l1_tlb_access_num + float(re.findall(r'\d+', lines[i])[2])
        l1_tlb_miss_num = l1_tlb_miss_num + float(re.findall(r'\d+', lines[i+1])[2])   
    l1_tlb_missrate = l1_tlb_miss_num / l1_tlb_access_num
    print('l1_tlb_missrate: {}'.format(l1_tlb_missrate))

    return mem_access_num, ptw_pool_missrate, l2_tlb_missrate, l1_tlb_missrate


def extract_design_2_or_3(lines, num_lanes):

    mem_access_num = re.findall(r'\d+', lines[0])[0]
    print('mem_access_num: {}'.format(mem_access_num))
    ptw_pool_missrate = float(re.findall(r'\d+', lines[1])[0]) / (float(re.findall(r'\d+', lines[2])[0])+eps)
    print('ptw_pool_missrate: {}'.format(ptw_pool_missrate))
    l2_tlb_missrate = float(re.findall(r'\d+', lines[4])[1]) / (float(re.findall(r'\d+', lines[3])[1])+eps)
    print('l2_tlb_missrate: {}'.format(l2_tlb_missrate))
    address_coalescer_missrate = float(re.findall(r'\d+', lines[6])[0]) / (float(re.findall(r'\d+', lines[5])[0])+eps)
    print('address_coalescer_missrate: {}'.format(address_coalescer_missrate))
    l1_tlb_access_num, l1_tlb_miss_num = eps, eps
    for i in range(7, 6+num_lanes*3, 3):
        # print('i: {}'.format(i))
        l1_tlb_access_num = l1_tlb_access_num + float(re.findall(r'\d+', lines[i])[2])
        l1_tlb_miss_num = l1_tlb_miss_num + float(re.findall(r'\d+', lines[i+1])[2]) 
    l1_tlb_missrate = l1_tlb_miss_num / l1_tlb_access_num
    print('l1_tlb_missrate: {}'.format(l1_tlb_missrate))

    return mem_access_num, ptw_pool_missrate, l2_tlb_missrate, address_coalescer_missrate, l1_tlb_missrate


def extract_design_4(lines, num_lanes):

    mem_access_num = re.findall(r'\d+', lines[0])[0]
    print('mem_access_num: {}'.format(mem_access_num))
    
    l1_pte_cache_missrate = float(re.findall(r'\d+', lines[2])[1]) / (float(re.findall(r'\d+', lines[1])[1])+eps)
    print('l1_pte_cache_missrate: {}'.format(l1_pte_cache_missrate))
    l2_pte_cache_missrate = float(re.findall(r'\d+', lines[4])[1]) / (float(re.findall(r'\d+', lines[3])[1])+eps)
    print('l2_pte_cache_missrate: {}'.format(l2_pte_cache_missrate))
    l3_pte_cache_missrate = float(re.findall(r'\d+', lines[6])[1]) / (float(re.findall(r'\d+', lines[5])[1])+eps)
    print('l3_pte_cache_missrate: {}'.format(l3_pte_cache_missrate))

    ptw_pool_missrate = float(re.findall(r'\d+', lines[7])[0]) / (float(re.findall(r'\d+', lines[8])[0])+eps)
    print('ptw_pool_missrate: {}'.format(ptw_pool_missrate))
    l2_tlb_missrate = float(re.findall(r'\d+', lines[10])[1]) / (float(re.findall(r'\d+', lines[9])[1])+eps)
    print('l2_tlb_missrate: {}'.format(l2_tlb_missrate))
    address_coalescer_missrate = float(re.findall(r'\d+', lines[12])[0]) / (float(re.findall(r'\d+', lines[11])[0])+eps)
    print('address_coalescer_missrate: {}'.format(address_coalescer_missrate))
    l1_tlb_access_num, l1_tlb_miss_num = eps, eps
    for i in range(13, 12+num_lanes*3, 3):
        # print('i: {}'.format(i))
        l1_tlb_access_num = l1_tlb_access_num + float(re.findall(r'\d+', lines[i])[2])
        l1_tlb_miss_num = l1_tlb_miss_num + float(re.findall(r'\d+', lines[i+1])[2]) 
    l1_tlb_missrate = l1_tlb_miss_num / l1_tlb_access_num
    print('l1_tlb_missrate: {}'.format(l1_tlb_missrate))

    return mem_access_num, l1_pte_cache_missrate, l2_pte_cache_missrate, l3_pte_cache_missrate, ptw_pool_missrate, l2_tlb_missrate, address_coalescer_missrate, l1_tlb_missrate

workload_matcher = {'gemm': 0, 'gups': 1, 'npb': 2, 'permutating': 3, 'stream': 4}
stream_matcher = {'add': 4, 'copy': 5}
lane_matcher = {'8': 0, '32': 1, '128': 2}
page_size_matcher = {'4096': 0, '2097152': 1}

def get_workload_index(workload_class, stream_class):

    index = workload_matcher[workload_class]
    assert index in [0, 1, 2, 3, 4]
    if index == 4:
        index = stream_matcher[stream_class]
    assert index in [0, 1, 2, 3, 4, 5]
    
    return index

def get_lane_index(num_lanes):
    return lane_matcher[num_lanes]

def get_page_size_index(page_size_bytes):
    return page_size_matcher[page_size_bytes]

def get_avg(a: list) -> float: 
    return sum(a) / len(a)

def processing_data():

    print('***Started Data Loading***')
    # nums_foreach_design = [0, 0, 0, 0]
    # mem_access_num_global = [[], [], [], []]
    # ptw_pool_missrate_global = [[], [], [], []]
    # l1_tlb_missrate_global = [[], [], [], []]
    # l2_tlb_missrate_global = [[], [], [], []]  # for each design respectively

    # mem_access_num_by_workload = [[[] for _ in range(6)] for _ in range(4)]
    # ptw_pool_missrate_by_workload = [[[] for _ in range(6)] for _ in range(4)]
    # l1_tlb_missrate_by_workload = [[[] for _ in range(6)] for _ in range(4)]
    # l2_tlb_missrate_by_workload = [[[] for _ in range(6)] for _ in range(4)]  # [design_class, workload_class]
    
    # mem_access_num_by_num_lanes = [[[] for _ in range(3)] for _ in range(4)]
    # ptw_pool_missrate_by_num_lanes = [[[] for _ in range(3)] for _ in range(4)]
    # l1_tlb_missrate_by_num_lanes = [[[] for _ in range(3)] for _ in range(4)]
    # l2_tlb_missrate_by_num_lanes = [[[] for _ in range(3)] for _ in range(4)] # [design_class, num_lanes_class]
    
    # mem_access_num_by_page_size = [[[] for _ in range(2)] for _ in range(4)] 
    # ptw_pool_missrate_by_page_size = [[[] for _ in range(2)] for _ in range(4)]
    # l1_tlb_missrate_by_page_size = [[[] for _ in range(2)] for _ in range(4)] 
    # l2_tlb_missrate_by_page_size = [[[] for _ in range(2)] for _ in range(4)] # [design_class, page_size_class]
    

    mem_access_num_dict = np.zeros([6, 4, 3, 2])
    ptw_pool_missrate_dict = np.zeros([6, 4, 3, 2])
    l2_tlb_missrate_dict = np.zeros([6, 4, 3, 2])
    l1_tlb_missrate_dict = np.zeros([6, 4, 3, 2]) # [workload_class, design_class, num_lanes_class, page_size_class]
    address_coalescer_missrate_dict = np.zeros([6, 3, 3, 2]) # [workload_class, design_class{2, 3, 4}, num_lanes_class, page_size_class]
    pte_cache_missrate_dict = np.zeros([6, 3, 2, 3]) # [workload_class, num_lanes_class, page_size_class, pte_cache{l1, l2, l3}] only for design_class{4}
    
    data_folder = os.path.join(os.getcwd(), 'cache_model/results')
    for filename in os.listdir(data_folder):
        if filename.split('_')[0] != 'design':
            continue
        design_class, page_size_bytes, workload_class, num_lanes, stream_class = extract_variables(filename)
        # nums_foreach_design[design_class-1] = nums_foreach_design[design_class-1] + 1
        with open(os.path.join(data_folder, filename), 'r') as f:
            lines = f.readlines()
            if design_class == 1:
                mem_access_num, ptw_pool_missrate, l2_tlb_missrate, l1_tlb_missrate = extract_design_1(lines, num_lanes) 
            elif (design_class == 2) or (design_class == 3):   
                mem_access_num, ptw_pool_missrate, l2_tlb_missrate, address_coalescer_missrate, l1_tlb_missrate = extract_design_2_or_3(lines, num_lanes)
            elif design_class == 4:
                mem_access_num, l1_pte_cache_missrate, l2_pte_cache_missrate, l3_pte_cache_missrate, ptw_pool_missrate, l2_tlb_missrate, address_coalescer_missrate, l1_tlb_missrate = extract_design_4(lines, num_lanes)
            else:
                raise NotImplementedError
            # l1_tlb_missrate_global[design_class-1].append(l1_tlb_missrate)
            # l2_tlb_missrate_global[design_class-1].append(l2_tlb_missrate)
            workload_index = get_workload_index(workload_class, stream_class)
            # l1_tlb_missrate_by_workload[design_class-1][index].append(l1_tlb_missrate)
            # l2_tlb_missrate_by_workload[design_class-1][index].append(l2_tlb_missrate)
            lane_index = get_lane_index(str(num_lanes))
            # l1_tlb_missrate_by_num_lanes[design_class-1][lane_index].append(l1_tlb_missrate)
            # l2_tlb_missrate_by_num_lanes[design_class-1][lane_index].append(l2_tlb_missrate)
            page_size_index = get_page_size_index(str(page_size_bytes))
            # l1_tlb_missrate_by_page_size[design_class-1][page_size_index].append(l1_tlb_missrate)
            # l2_tlb_missrate_by_page_size[design_class-1][page_size_index].append(l2_tlb_missrate)
            mem_access_num_dict[workload_index, design_class-1, lane_index, page_size_index] = mem_access_num
            ptw_pool_missrate_dict[workload_index, design_class-1, lane_index, page_size_index] = ptw_pool_missrate
            l2_tlb_missrate_dict[workload_index, design_class-1, lane_index, page_size_index] = l2_tlb_missrate
            l1_tlb_missrate_dict[workload_index, design_class-1, lane_index, page_size_index] = l1_tlb_missrate
            if design_class != 1:
                address_coalescer_missrate_dict[workload_index, design_class-2, lane_index, page_size_index] = address_coalescer_missrate
            if design_class == 4:
                pte_cache_missrate_dict[workload_index, lane_index, page_size_index] = [l1_pte_cache_missrate, l2_pte_cache_missrate, l3_pte_cache_missrate]

    print('mem_access_num_dict: {}'.format(mem_access_num_dict))
    print('mem_access_num_dict.shape: {}'.format(mem_access_num_dict.shape))
    print('ptw_pool_missrate_dict: {}'.format(ptw_pool_missrate_dict))
    print('l2_tlb_missrate_dict: {}'.format(l2_tlb_missrate_dict))
    print('l1_tlb_missrate_dict: {}'.format(l1_tlb_missrate_dict))
    print('address_coalescer_missrate_dict: {}'.format(address_coalescer_missrate_dict))
    print('pte_cache_missrate_dict: {}'.format(pte_cache_missrate_dict))


    # for i in range(4):
    #     l1_tlb_missrate_global[i] = get_avg(l1_tlb_missrate_global[i])
    #     l2_tlb_missrate_global[i] = get_avg(l2_tlb_missrate_global[i])
    #     for j in range(6):
    #         l1_tlb_missrate_by_workload[i][j] = get_avg(l1_tlb_missrate_by_workload[i][j])
    #         l2_tlb_missrate_by_workload[i][j] = get_avg(l2_tlb_missrate_by_workload[i][j])
    #     for j in range(3):
    #         l1_tlb_missrate_by_num_lanes[i][j] = get_avg(l1_tlb_missrate_by_num_lanes[i][j])
    #         l2_tlb_missrate_by_num_lanes[i][j] = get_avg(l2_tlb_missrate_by_num_lanes[i][j])
    #     for j in range(2):
    #         l1_tlb_missrate_by_page_size[i][j] = get_avg(l1_tlb_missrate_by_page_size[i][j])
    #         l2_tlb_missrate_by_page_size[i][j] = get_avg(l2_tlb_missrate_by_page_size[i][j])
    
    # print('l1_tlb_missrate_global: {}'.format(l1_tlb_missrate_global))
    # print('l2_tlb_missrate_global: {}'.format(l2_tlb_missrate_global))
    # print('l1_tlb_missrate_by_workload: {}'.format(l1_tlb_missrate_by_workload))
    # print('l2_tlb_missrate_by_workload: {}'.format(l2_tlb_missrate_by_workload))
    # print('l1_tlb_missrate_by_num_lanes: {}'.format(l1_tlb_missrate_by_num_lanes))
    # print('l2_tlb_missrate_by_num_lanes: {}'.format(l2_tlb_missrate_by_num_lanes))
    # print('l1_tlb_missrate_by_page_size: {}'.format(l1_tlb_missrate_by_page_size))
    # print('l2_tlb_missrate_by_page_size: {}'.format(l2_tlb_missrate_by_page_size))
    print('***Finished Data Loading***')

    return mem_access_num_dict, ptw_pool_missrate_dict, l2_tlb_missrate_dict, l1_tlb_missrate_dict, address_coalescer_missrate_dict, pte_cache_missrate_dict
