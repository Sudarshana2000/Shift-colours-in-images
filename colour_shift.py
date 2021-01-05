import cv2
import numpy as np
from sklearn.cluster import KMeans

num_clusters=5

# Segregate the pixel locations based on major colour variants
def getClusters(image):
    # Converting the colour space into hsv so that shades retain in the image
    image=cv2.cvtColor(image,cv2.COLOR_BGR2HSV)
    image=image.reshape((image.shape[0]*image.shape[1],3))
    kmeans=KMeans(n_clusters=num_clusters,init='k-means++',max_iter=100,n_init=10,verbose=0,random_state=1000)
    kmeans.fit(image)
    clusters=kmeans.cluster_centers_
    labels=kmeans.labels_
    clusters=clusters.astype(int)
    return clusters,labels
 
# Order the pixel-cluster colour variants in descending order of their count  
def getOrder(labels):
    order={}
    unique,count=np.unique(labels,return_counts=True)
    for i in range(len(unique)):
        order[unique[i]]=count[i]
    return sorted(order,key=order.get,reverse=True)
 
# Create a colour map to track conversions between source and target 
def getColourMap(sCluster,tCluster,sOrder,tOrder):
    colour_map={}
    for i in range(num_clusters):
        h=sCluster[sOrder[i]][0]
        s=sCluster[sOrder[i]][1] - tCluster[tOrder[i]][1]
        v=sCluster[sOrder[i]][2] - tCluster[tOrder[i]][2]
        colour_map[i]=[h,s,v]
    return colour_map

# Shift the colours from source to target without messing up with the shades    
def ColourShift(target,colour_map,tLabel,tOrder):
    target=cv2.cvtColor(target,cv2.COLOR_BGR2HSV)
    tLabel=tLabel.reshape((target.shape[0],target.shape[1]))
    for i in range(target.shape[0]):
        for j in range(target.shape[1]):
            hsv=target[i,j]
            label=tLabel[i,j]
            mapping=colour_map[label]
            h=mapping[0]
            # Discard the white and grey regions
            if (0<=hsv[1]<=5 and 128<=hsv[2]<=255) or (0<=hsv[1]<=175 and 0<=hsv[2]<=127):
                s=hsv[1]
                v=hsv[2]
            else:
                s=hsv[1]+mapping[1]
                v=hsv[2]+mapping[2]
            # Out of bound values are set to their corresponding extremities
            if h<0:
                h=0
            if s<0:
                s=0
            if v<0:
                v=0
            if h>180:
                h=180
            if s>255:
                s=255
            if v>255:
                v=255
            target[i,j][0]=h
            target[i,j][1]=s
            target[i,j][2]=v
    target=cv2.cvtColor(target,cv2.COLOR_HSV2BGR)
    return target

# Main function    
def process(source,target,n):
    global num_clusters
    num_clusters=n
    source=cv2.resize(source,(640,640))
    target=cv2.resize(target,(640,640))
    sCluster,sLabel=getClusters(source)
    tCluster,tLabel=getClusters(target)
    sOrder=getOrder(sLabel)
    tOrder=getOrder(tLabel)
    colour_map=getColourMap(sCluster, tCluster, sOrder, tOrder)
    output=ColourShift(target,colour_map,tLabel,tOrder)
    return output

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('source', help='source image path')
    parser.add_argument('target', help='target image path')
    parser.add_argument('output', help='output image path')
    parser.add_argument('n', help='number of clusters')
    args = parser.parse_args()
    source = cv2.imread(args.source)
    target = cv2.imread(args.target)
    output = process(source, target, n)
    cv2.imwrite(args.output, output)