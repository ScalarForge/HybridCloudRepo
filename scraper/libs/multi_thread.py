import concurrent.futures

def multi_thread(function, data_list, num_threads=4):
    '''Given a function that performs an action on one piece of data at a time, and a list of data, multi-thread the operation'''
    
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        
        futures_to_data = {executor.submit(function, data): data for data in data_list}
        for future in concurrent.futures.as_completed(futures_to_data):
            try:
                orig_input = futures_to_data[future]
                results.append((orig_input, future.result()))
            except Exception as exc:
                print('%r generated an exception: %s' % (orig_input, exc))
                
    return results