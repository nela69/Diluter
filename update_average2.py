from os import path, listdir
import numpy as np
import imutils
import cv2

######################################################
###  updating average for background extraction    ###
######################################################

def updateAverage(no_cycl, pumptime = 1000, coeff = 0.1):

    impath = './testimages/color_test0'
    bkg_array = cv2.imread(impath + '0.png')
    avg_coeff = 1/(no_cycl + 1)
    if no_cycl >= 0:
        # print(np.min(np.min(bkg_array)),np.max(np.max(bkg_array)))
        for i in range(no_cycl):
            img_file = impath + str(i+1) + '.png'
            print(img_file)
            bkg_array = cv2.addWeighted(bkg_array, 1 - avg_coeff,  cv2.imread(img_file), avg_coeff, 0)
            print('Cumulative mean: ' + str(np.mean(np.mean(bkg_array))))

        print('Average mean: ' + str(np.mean(np.mean(bkg_array))))
        average_updated = True
#        print(np.mean(np.mean(bkg_array)))
#        print(np.min(np.min(bkg_array)),np.max(np.max(bkg_array)))
#        cv2.imshow('background', np.multiply(bkg_array.astype(float), 1/255))
        cv2.imshow('background', bkg_array)
        cv2.waitKey(0)
        ref_file = impath + '8.png'
#        bkg_extracted = np.subtract(cv2.imread(ref_file).astype(float), bkg_array)
        bkg_extracted = cv2.addWeighted(cv2.imread(ref_file), -1, bkg_array , 1 , 0)
        cv2.imshow('extracted', bkg_extracted)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

        print("Average updated: " + str(average_updated))

'''
    elif average_updated == True:
        bkg_array = np.array(np.add(np.multiply(bkg_array.astype(float), (1-coeff)), np.multiply(vs.read().astype(float), coeff)).astype(int), np.uint8)
    else:
        print('Background average not initialized')
'''

updateAverage(7)
