#import matplotlib.pyplot as plt

import re
import os
import matplotlib.pyplot as plt
import numpy as np


eps = 0.000000001

def extract_variables(filename):

    print('extracting file: {}'.format(filename))
    info = filename.split('_')
    design_class, page_size_bytes, workload_class = info[1], info[2], info[3]
    if (workload_class == 'gemm') or (workload_class == 'gups'):
        num_lanes = info[4]
    elif (workload_class == 'npb') or (workload_class == 'permutating') or (workload_class == 'stream'):
        num_lanes = info[5]
    else:
        raise NotImplementedError
    design_class, page_size_bytes, num_lanes = int(design_class), int(page_size_bytes), int(num_lanes)

    return design_class, page_size_bytes, workload_class, num_lanes


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

    return l1_pte_cache_missrate, l2_pte_cache_missrate, l3_pte_cache_missrate, ptw_pool_missrate, l2_tlb_missrate, address_coalescer_missrate, l1_tlb_missrate


def get_tlb_missrates():

    print('***Started Data Loading***')
    nums_foreach_design = [0, 0, 0, 0]
    l1_tlb_missrate_global = [[], [], [], []]  # for each design respectively
    l2_tlb_missrate_global = [[], [], [], []]  # for each design respectively
    data_folder = os.path.join(os.getcwd(), 'cache_model/results')
    for filename in os.listdir(data_folder):
        if filename.split('_')[0] != 'design':
            continue
        design_class, page_size_bytes, workload_class, num_lanes = extract_variables(filename)
        nums_foreach_design[design_class-1] = nums_foreach_design[design_class-1] + 1
        with open(os.path.join(data_folder, filename), 'r') as f:
            lines = f.readlines()
            if design_class == 1:
                mem_access_num, ptw_pool_missrate, l2_tlb_missrate, l1_tlb_missrate = extract_design_1(lines, num_lanes) 
            elif (design_class == 2) or (design_class == 3):   
                mem_access_num, ptw_pool_missrate, l2_tlb_missrate, address_coalescer_missrate, l1_tlb_missrate = extract_design_2_or_3(lines, num_lanes)
            elif design_class == 4:
                l1_pte_cache_missrate, l2_pte_cache_missrate, l3_pte_cache_missrate, ptw_pool_missrate, l2_tlb_missrate, address_coalescer_missrate, l1_tlb_missrate = extract_design_4(lines, num_lanes)
            else:
                raise NotImplementedError
            l1_tlb_missrate_global[design_class-1].append(l1_tlb_missrate)
            l2_tlb_missrate_global[design_class-1].append(l2_tlb_missrate)
        
    for i in range(4):
        l1_tlb_missrate_global[i] = sum(l1_tlb_missrate_global[i]) / len(l1_tlb_missrate_global[i])
        l2_tlb_missrate_global[i] = sum(l2_tlb_missrate_global[i]) / len(l2_tlb_missrate_global[i])
    print('l1_tlb_missrate_global: {}'.format(l1_tlb_missrate_global))
    print('l2_tlb_missrate_global: {}'.format(l2_tlb_missrate_global))
    print('***Finished Data Loading***')

    return l1_tlb_missrate_global, l2_tlb_missrate_global
