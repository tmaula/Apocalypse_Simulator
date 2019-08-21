##CBE5790, Final Project: Apocalypse Simulator.
##Project Description: Track migration pattern in an apocalypse. PRgram uses dead zone
##boundary conditions. Program runs for 60 days.
##created by: T. Maula, 12/13/15
##edited:

import numpy as np
import matplotlib.pyplot as plt
#from matplotlib import colors
import matplotlib
import matplotlib.colors as mcol

def plague(heterogeneity, paniclevel):
    #DEFAULT SETTINGS
    Nrho = 500 #average population number density
    krates = np.array([6.25e-7, 10]) #rxn rates
    city = np.zeros((22,22)) #cells for total population, 400km*km + boundaries
    cityH = np.zeros((22,22)) #cells for healthy pop.
    cityS = np.zeros((22,22)) #cells for sick pop.
    cityD = np.zeros((22,22)) #cells for dead
    day = 0
    finday = 30
    # FUNCTIONS TO ASSIGN POPULATION PER CELL
    #function to assign population in city
    def dispersion(Nrho, heterogeneity, city):
        if heterogeneity == 0:
            city[1:21,1:21].fill(Nrho)
        else:
            devdir = np.power(-1, (np.random.randint(0, 9, [city.shape[0]-2,city.shape[1]-2])))
            H = np.random.uniform(0, heterogeneity, [city.shape[0]-2,city.shape[1]-2])
            city[1:21, 1:21] = np.trunc(np.multiply(devdir, H)*Nrho) + Nrho
        return city
    #function to assign sick and dead population, decide where to migrate
    def plagueassign(city, cityH, cityS, cityD, krates, paniclevel, *args):
        #neighborhood array creating function
        def doom(city):
            neighbors = np.zeros([20,20,4])
            neighbors[:,:,0] = city[1:21,0:20] #west
            neighbors[:,:,1] = city[1:21,2:22] #east
            neighbors[:,:,2] = city[0:20,1:21] #north
            neighbors[:,:,3] = city[2:22,1:21] #south
            return neighbors
        #create neighborhood arrays
        NH = doom(cityH)
        NS = doom(cityS)
        ND = doom(cityD)
        #preallocate arrays
        r_sick = np.zeros((city.shape[0], city.shape[1]))
        r_dead = np.zeros((city.shape[0], city.shape[1]))
        r_tot = np.zeros((city.shape[0], city.shape[1]))
        Psick = np.zeros((city.shape[0], city.shape[1]))
        Pdead = np.zeros((city.shape[0], city.shape[1]))
        #assign sick and dead
        for i in range(0,city.shape[0]-2):
            for j in range(0,city.shape[1]-2):
                #illness and death rate per 1 km*km
                r_sick[i, j] = krates[0]*np.sum(NH[i,j,:])*np.sum(NS[i,j,:])/2.0
                r_dead[i, j] = krates[1]*np.sum(NS[i,j,:])
                r_tot[i, j] = r_sick[i, j] + r_dead[i, j]
                #calculate probability of anyone person getting sick or dying
                if r_tot[i,j] > 0.0:
                   #update city population
                   sick = r_sick[i, j]
                   dead = r_dead[i, j]
                else:
                    sick = 0
                    dead = 0
                cityH[i,j] -= sick
                cityS[i,j] += (sick - dead)
                cityD[i,j] += dead
                city[i,j] = cityS[i,j] + cityH[i,j]
        #migrate people based on the number of sick and dead
        NH = doom(cityH)
        NS = doom(cityS)
        ND = doom(cityD)
        migrate_fracH = np.zeros((city.shape[0], city.shape[1]))
        migrate_fracS = np.zeros((city.shape[0], city.shape[1]))
        for m in range(1, city.shape[0]-1):
            for n in range(1, city.shape[0]-1):
                for p in range(0, 4):
                    if p==0:
                        parapop = cityS[m,n] + cityD[m,n]
                        paradise = -1
                        #find location with minimum sick and dead people
                    if NS[m-1,n-1,p]+ ND[m-1,n-1,p] < parapop: 
                        paradise = p
                        parapop = NS[m-1,n-1,p]+ ND[m-1,n-1,p] 
                        healthy = int(cityH[m,n]*paniclevel/11.0)
                        sick = int(cityS[m, n]*paniclevel/11.0)
                        tally = 1
                #migrate from current location into location w/ less sick people 
                if paradise >= 0:
                    if paradise == 0: #west 
                        migrate_fracH[m,n] -= healthy
                        migrate_fracS[m,n] -= sick
                        migrate_fracH[m,n-1] += healthy 
                        migrate_fracS[m,n-1] += sick
                    elif paradise == 1: #east
                        migrate_fracH[m,n] -= healthy 
                        migrate_fracS[m,n] -= sick
                        migrate_fracH[m,n+1] += healthy 
                        migrate_fracS[m,n+1] += sick                           
                    elif paradise == 2: #north
                        migrate_fracH[m,n] -= healthy 
                        migrate_fracS[m,n] -= sick
                        migrate_fracH[m+1,n] += healthy 
                        migrate_fracS[m+1,n] += sick                          
                    elif paradise == 3: #south
                        migrate_fracH[m,n] -= healthy 
                        migrate_fracS[m,n] -= sick
                        migrate_fracH[m-1,n] += healthy 
                        migrate_fracS[m-1,n] += sick
        for q in range(1, city.shape[0]-1):
            for r in range(1, city.shape[0]-1):
                cityH[q,r] += migrate_fracH[q,r]
                cityS[q,r] += migrate_fracS[q,r]
                city[q,r] = cityH[q,r] + cityS[q,r]
        return city, cityH, cityS, cityD
    #BEGINNING OF PROGRAM 
    #initialize populations
    city = dispersion(Nrho, heterogeneity, city)
    init_pop = np.sum(city)
    curr_pop = np.sum(init_pop)
    cityS[15,15] = 50
    cityS[8,9] = 50
    
    cityH = np.subtract(city, cityS)
    
    #create plotting function
    lvTmp = np.linspace(0, 1.0, 1000)
    cmTmp = matplotlib.cm.Paired(lvTmp)
    newCmap = mcol.ListedColormap(cmTmp)
    
    def makeFig():
        im = plt.imshow(cityD, cmap=newCmap, interpolation='nearest')
        plt.title('Migration Map\nInitial Pop.: '+str(init_pop)+'\nCurrent Pop.: '+str(curr_pop)+'\nDay: '+str(day))
        plt.autoscale()
        if day == 30:
            plt.colorbar()
        
    fig = plt.figure()
    #run the simulation
    for i in range(0, finday+1):
        #plot progress
        if curr_pop <=0:
            break
        makeFig()
        plt.pause(0.1)
        #assign people who become ill or die and update population nd where to migrate
        city, cityH, cityS, cityD = plagueassign(city, cityH, cityS, cityD, krates, paniclevel)
        curr_pop = np.sum(city)

        day+=1

    plt.show()
    
    return
