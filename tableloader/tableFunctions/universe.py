# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
import os
import glob
import yaml
from sqlalchemy import Table


def importyaml(connection,metadata,sourcePath):

    print "Importing Universe Data"

    mapCelestialStatistics =  Table('mapCelestialStatistics', metadata)
    mapConstellationJumps =  Table('mapConstellationJumps', metadata)
    mapConstellations =  Table('mapConstellations', metadata) # done
    mapDenormalize =  Table('mapDenormalize', metadata)
    mapJumps =  Table('mapJumps', metadata)
    mapLandmarks =  Table('mapLandmarks', metadata)
    mapLocationScenes =  Table('mapLocationScenes', metadata)
    mapLocationWormholeClasses =  Table('mapLocationWormholeClasses', metadata)
    mapRegionJumps =  Table('mapRegionJumps', metadata)
    mapRegions =  Table('mapRegions', metadata) # done
    mapSolarSystemJumps =  Table('mapSolarSystemJumps', metadata)
    mapSolarSystems =  Table('mapSolarSystems', metadata)
    invNames =  Table('invNames', metadata)
    
    
    
    regions=glob.glob(os.path.join(sourcePath,'fsd','universe','*','*','region.staticdata'))
    for regionfile in regions:
        head, tail = os.path.split(regionfile)
        print "Importing Region {}".format(head)
        trans = connection.begin()
        with open(regionfile,'r') as yamlstream:
            region=yaml.load(yamlstream,Loader=yaml.CSafeLoader)
        regionname=connection.execute(
            invNames.select().where( invNames.c.itemID == region['regionID'] )
        ).fetchall()[0]['itemName']
        print "Region {}".format(regionname)
        connection.execute(mapRegions.insert(),
                            regionID=region['regionID'],
                            regionName=regionname,
                            x=region['center'][0],
                            y=region['center'][1],
                            z=region['center'][2],
                            xMax=region['max'][0],
                            yMax=region['max'][1],
                            zMax=region['max'][2],
                            xMin=region['min'][0],
                            yMin=region['min'][1],
                            zMin=region['min'][2],
                            factionID=region.get('factionID'))
        connection.execute(mapLocationScenes.insert(),
                            locationID=region['regionID'],
                            graphicID=region['nebula'])
        print "Importing Constellations."
        constellations=glob.glob(os.path.join(head,'*','constellation.staticdata'))
        for constellationfile in constellations:
            chead, tail = os.path.split(constellationfile)
            with open(constellationfile,'r') as yamlstream:
                constellation=yaml.load(yamlstream,Loader=yaml.CSafeLoader)
            constellationname=connection.execute(
                invNames.select().where( invNames.c.itemID == constellation['constellationID'] )
            ).fetchall()[0]['itemName']
            print "Constellation {}".format(constellationname)
            connection.execute(mapConstellations.insert(),
                                regionID=region['regionID'],
                                constellationID=constellation['constellationID'],
                                constellationName=constellationname,
                                x=constellation['center'][0],
                                y=constellation['center'][1],
                                z=constellation['center'][2],
                                xMax=constellation['max'][0],
                                yMax=constellation['max'][1],
                                zMax=constellation['max'][2],
                                xMin=constellation['min'][0],
                                yMin=constellation['min'][1],
                                zMin=constellation['min'][2],
                                radius=constellation['radius'])
            systems=glob.glob(os.path.join(chead,'*','solarsystem.staticdata'))
            print "Importing Systems"
            for systemfile in systems:
                with open(systemfile,'r') as yamlstream:
                    system=yaml.load(yamlstream,Loader=yaml.CSafeLoader)
                systemname=connection.execute(
                    invNames.select().where( invNames.c.itemID == system['solarSystemID'] )
                ).fetchall()[0]['itemName']
                print "System {}".format(systemname)
                connection.execute(mapSolarSystems.insert(),
                                    regionID=region['regionID'],
                                    constellationID=constellation['constellationID'],
                                    solarSystemID=system['solarSystemID'],
                                    solarSystemName=systemname,
                                    x=system['center'][0],
                                    y=system['center'][1],
                                    z=system['center'][2],
                                    xMax=system['max'][0],
                                    yMax=system['max'][1],
                                    zMax=system['max'][2],
                                    xMin=system['min'][0],
                                    yMin=system['min'][1],
                                    zMin=system['min'][2],
                                    luminosity=system['luminosity'],
                                    border=system['border'],
                                    fringe=system['fringe'],
                                    corridor=system['corridor'],
                                    hub=system['hub'],
                                    international=system['international'],
                                    regional=system['regional'],
                                    security=system['security'],
                                    factionid=system.get('factionID'),
                                    radius=system['radius'],
                                    sunTypeID=system['sunTypeID'],
                                    securityClass=system.get('securityClass'))
                print "Importing Statistics"
                for planet in system.get('planets'):
                    system['planets'][planet]['statistics']['celestialID']=planet
                    connection.execute(mapCelestialStatistics.insert(),
                                        system['planets'][planet]['statistics'])
                    for belt in system['planets'][planet].get('asteroidBelts',[]):
                        system['planets'][planet]['asteroidBelts'][belt]['statistics']['celestialID']=belt
                        connection.execute(mapCelestialStatistics.insert(),
                                        system['planets'][planet]['asteroidBelts'][belt]['statistics'])
                    for moon in system['planets'][planet].get('moons',[]):
                        system['planets'][planet]['moons'][moon]['statistics']['celestialID']=moon
                        connection.execute(mapCelestialStatistics.insert(),
                                        system['planets'][planet]['moons'][moon]['statistics'])

            
            
            
        trans.commit()