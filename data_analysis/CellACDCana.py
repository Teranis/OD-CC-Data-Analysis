import os
from core import loadcsv
import pandas as pd
def checkingcompleteness(root_paths):
    errorlist = []
    channels_master = []
    for root_path in root_paths:
        folder_list = os.listdir(root_path)
        print('\nFound Positions:')
        print(folder_list)
        folder_list_CellACDC = [os.path.join(root_path, folder_name, 'Images') for folder_name in folder_list]
        folder_list_spotMAX = [os.path.join(root_path, folder_name, 'spotMAX_output') for folder_name in folder_list]
        print('\n\n\n\n~~~~~~~~~~ Checking CellACDC output! ~~~~~~~~~~')
        for folder_name in folder_list_CellACDC:
            print('\n\n********** Checking folder: '+folder_name+ ' **********')

            searchfiles = ("acdc_output.csv", "align_shift.npy", "custom_annot_params.json", "custom_combine_metrics.ini", "dataPrepROIs_coords.csv", "dataPrep_bkgrROIs.json",  "last_tracked_i.txt", "metadata.csv", "metadataXML.txt", "segm.npz")
            boolinalist = [False]*len(searchfiles)
            searchfiles = list(map(list, zip(searchfiles, boolinalist)))
            try:
                files = os.listdir(folder_name)
            except:
                print('No CellACDC folder found!')
                errorlist.append(folder_name)
                continue

            #printl(files)
            #printl(files, pretty=True)
            for i, (searchname, boolian) in enumerate(searchfiles):
                for file in files:
                    if file.endswith(searchname):
                        #print('found smth')
                        if boolian == False:
                            searchfiles[i][1] = True
                        else:
                            print('Found another copy of: '+searchname + '\nin: '+ folder_name+'\n')
                            errorlist.append(folder_name)

            channels = []
            files = os.listdir(folder_name)
            for file in files:
                if file.endswith('.tif') or file.endswith('.npz'):
                    file = file.split(".")[0]
                    if not file.endswith('segm') and not file.endswith('bkgrRoiData') and not file.endswith('segm_mask'):
                        if file.endswith('_aligned'):
                            file = file[:-len('_aligned')]
                        file = file.split('_')[-1]
                        if file not in channels:
                            channels.append(file)
            print('\nFound channels:')
            print(channels, end=' ')
            if channels_master == []:
                channels_master = channels.copy()
                print('***Set expected channels to: ', end='')
                print(channels_master)
            elif channels != channels_master:
                print('~+~+~+~+~+~+ WARNING: ~+~+~+~+~+~+ \nChannels of: ' + folder_name + ' do NOT match the first checked pos\' channel.')
                errorlist.append(folder_name)
            else:
                print('Channels seem good!')
            
            
            for channel in channels:
                searchchanfiles = (channel+"_aligned_bkgrRoiData.npz", channel+"_aligned.npz", channel+".tif")
                #print(files)
                #print(searchchanfiles)
                boolinalist = [False]*len(searchchanfiles)
                searchchanfiles = list(map(list, zip(searchchanfiles, boolinalist)))
                #print(searchchanfiles)
                for i, (searchname, boolian) in enumerate(searchchanfiles):
                    for file in files:
                        #printl(searchname)
                        if file.endswith(searchname):
                            if boolian == False:
                                searchchanfiles[i][1] = True
                            else:
                                print('Found another copy of: '+searchname + '\nin: '+ folder_name+'\n')
                                errorlist.append(folder_name)

                tifornpz = False
                #print(searchchanfiles)
                #print(searchfiles)
                for searchname, boolian in searchchanfiles:
                    if searchname.endswith('_aligned.npz') or searchname.endswith('.tif'):
                        tifornpz = True
                if tifornpz == False:
                    print('~+~+~+~+~+~+ CRITICAL: ~+~+~+~+~+~+ \nNo .tif or .npz for: ' + channel + '\nin: '+ folder_name+'\n')
                    errorlist.append(folder_name)
                #print(searchchanfiles)
                for searchname, boolian in searchchanfiles:
                    if boolian == False:
                        print('No copy of: '+searchname + '\nin: '+ folder_name+'\n')
                        errorlist.append(folder_name)
            backupload = False
            #print(searchfiles)
            for searchname, boolian in searchfiles:
                if boolian == False:
                    if searchname == 'acdc_output.csv' or searchname == 'segm.npz':
                        backupload = True
                        print('~+~+~+~+~+~+ CRITICAL: ~+~+~+~+~+~+ \nNo copy of: ' + searchname + '\nin: '+ folder_name+'\n')
                        errorlist.append(folder_name)
                    else:
                        print('No copy of: '+searchname + '\nin: '+ folder_name+'\n')
                        errorlist.append(folder_name)
            for file in os.listdir(folder_name):
                if file.endswith('_acdc_output.csv'):
                    acdc_output = loadcsv(os.path.join(folder_name, file))
                    break
            if 'cell_cycle_stage' in acdc_output:
                print('Cell cycle annotation is present!')
            elif 'cell_cycle_stage' not in acdc_output:
                print('~+~+~+~+~+~+ CRITICAL: ~+~+~+~+~+~+ \nNo copy of: ' + searchname + '\nin: '+ folder_name+'\n')
                errorlist.append(folder_name)
            backupload = True
            if backupload == True:
                for file in os.listdir(folder_name):
                    if file == "recovery":
                        while True:
                            answer = input('Found recovery. Do you want to restore?([y]/n)')
                            answer = answer.lower()
                            if answer == "y":
                                h5_filepath = os.path.join(folder_name, 'recovery')
                                backup_name = os.listdir(h5_filepath)[0] ###########
                                h5_filepath = os.path.join(h5_filepath, backup_name)
                                print(h5_filepath)
                                while True:
                                    answer = input('Do you want to recover from this file?([y]/n)')
                                    answer = answer.lower()
                                    if answer == "y":
                                        with pd.HDFStore(h5_filepath, 'r') as hdf:
                                            keys = hdf.keys()
                                            dfkeys = pd.DataFrame(keys)
                                            dfkeys.sort_values(ascending=False)
                                            df = hdf[dfkeys.iloc()[0]]
                                            df.to_csv(os.path.join(folder_name, backup_name.rstrip('.h5')+'backuprestored.csv'))
                                    elif answer == "n":
                                        break
                                    else:
                                        print('That input confused me a bit! please make sure to type \'y\' or \'n\'')
                                        exit()
                            else:
                                print('That input confused me a bit! please make sure to type \'y\' or \'n\'')
                                exit()
        print('\n\n~~~~~~~~~~ Done checking CellACDC output! ~~~~~~~~~~')
        print('\n\n\n\n~~~~~~~~~~ Checking SpotMAX output! ~~~~~~~~~~')
        for folder_name in folder_list_spotMAX:
            print('\n\n********** Checking folder: ' + folder_name + ' **********')
            try:
                files = os.listdir(folder_name)
            except:
                print('No SpotMAX folder found!')
                errorlist.append(folder_name)
                continue
            for file in files:
                searchfiles = ("detected_spots_aggregated.csv", "analysis_parameters.ini")
                boolinalist = [False]*len(searchfiles)
                searchfiles = list(map(list, zip(searchfiles, boolinalist)))
                for i, (searchname, boolian) in enumerate(searchfiles):
                    for file in files:
                        if file.endswith(searchname):
                            #print('found smth')
                            if boolian == False:
                                searchfiles[i][1] = True
                            else:
                                print('Found another copy of: '+searchname + '\nin: '+ folder_name+'\n')
                for searchname, boolian in searchfiles:
                    if boolian == False:
                        print('~+~+~+~+~+~+ CRITICAL: ~+~+~+~+~+~+ \nNo copy of: ' + searchname + '\nin: '+ folder_name+'\n')
                        errorlist.append(folder_name)
    if errorlist != []:
        errorlistunique = []
        for error in errorlist:
            if error not in errorlistunique:
                errorlistunique.append(error)
        print("~+~+~+~+~+~+ ERRORS FOUND: ~+~+~+~+~+~+")
        print("\n".join(errorlistunique))