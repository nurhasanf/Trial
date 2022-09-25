import ee

#  Kalibrasi Landsat 4 Raw
def L4Raw(image):
    B1 = image.select('B1').multiply(0.0010178).add(-0.003406)
    B2 = image.select('B2').multiply(0.0023169).add(-0.007249)
    B3 = image.select('B3').multiply(0.0020655).add(-0.004471)
    B4 = image.select('B4').multiply(0.0025893).add(-0.007052)
    B5 = image.select('B5').multiply(0.0017226).add(-0.006818)
    B6 = image.select('B6').multiply(0.055375).add(1.18243)
    B7 = image.select('B7').multiply(0.0024189).add(-0.007921)

    return image.addBands(B1, None, True) \
                .addBands(B2, None, True) \
                .addBands(B3, None, True) \
                .addBands(B4, None, True) \
                .addBands(B5, None, True) \
                .addBands(B6, None, True) \
                .addBands(B7, None, True)

# Kalibrasi Landsat 5 Raw
def L5Raw(image):
    B1 = image.select('B1').multiply(0.0011129).add(-0.003633)
    B2 = image.select('B2').multiply(0.0024223).add(-0.007625)
    B3 = image.select('B3').multiply(0.0022579).add(-0.004788)
    B4 = image.select('B4').multiply(0.0027329).add(-0.007443)
    B5 = image.select('B5').multiply(0.0018504).add(-0.007539)
    B6 = image.select('B6').multiply(0.055375).add(1.18243)
    B7 = image.select('B7').multiply(0.0025686).add(0.065551)

    return image.addBands(B1, None, True) \
                .addBands(B2, None, True) \
                .addBands(B3, None, True) \
                .addBands(B4, None, True) \
                .addBands(B5, None, True) \
                .addBands(B6, None, True) \
                .addBands(B7, None, True)

# Kalibrasi Landsat 7 Raw
def L7Raw(image):
    B1 = image.select('B1').multiply(0.0012395).add(-0.011108)
    B2 = image.select('B2').multiply(0.0013948).add(-0.012569)
    B3 = image.select('B3').multiply(0.001321).add(-0.011946)
    B4 = image.select('B4').multiply(0.0019358).add(-0.017368)
    B5 = image.select('B5').multiply(0.0018458).add(-0.01647)
    B6_VCID_1 = image.select('B6_VCID_1').multiply(0.067087).add(-0.06709)
    B6_VCID_2 = image.select('B6_VCID_2').multiply(0.037205).add(3.1628)
    B7 = image.select('B7').multiply(0.0017485).add(-0.015689)
    B8 = image.select('B8').multiply(0.0023969).add(-0.013944)

    return image.addBands(B1, None, True) \
                .addBands(B2, None, True) \
                .addBands(B3, None, True) \
                .addBands(B4, None, True) \
                .addBands(B5, None, True) \
                .addBands(B6_VCID_1, None, True) \
                .addBands(B6_VCID_2, None, True) \
                .addBands(B7, None, True) \
                .addBands(B8, None, True)

# Kalibrasi Landsat 8 Raw
def L8Raw(image):
    opticBands = image.select('B[1-9]').multiply(0.00002).add(-0.1)
    thermalBands = image.select('B.[10-11]').multiply(0.0003342).add(0.1)
    return image.addBands(opticBands, None, True) \
                .addBands(thermalBands, None, True)

# Kalibrasi Landsat 9 Raw
def L9Raw(image):
    opticBands = image.select('B[1-9]').multiply(0.00002).add(-0.1)
    thermalBand10 = image.select('B10').multiply(0.00038).add(0.1)
    thermalBand11 = image.select('B11').multiply(0.000349).add(0.1)
    return image.addBands(opticBands, None, True) \
                .addBands(thermalBand10, None, True) \
                .addBands(thermalBand11, None, True)

# Kalibrasi Landsat Surface Reflectance
def SR(image):
    opticBands = image.select('SR_B.').multiply(0.0000275).add(-0.2)
    thermalBands = image.select('ST_B.*').multiply(0.00341802).add(149.0)
    return image.addBands(opticBands, None, True) \
                .addBands(thermalBands, None, True)

def mask(image):
    qa = image.select('QA_PIXEL')
    mask_cloud = qa.bitwiseAnd(1 << 3).eq(0)
    mask_shadow = qa.bitwiseAnd(1 << 4).eq(0)
    
    return image.updateMask(mask_cloud) \
                .updateMask(mask_shadow)


def ndvi(satelliteNumber):
    
    def wrap(image):
        
        # choose bands
        nir = ee.String(ee.Algorithms.If(satelliteNumber == 'L8', 'SR_B5',
                        ee.Algorithms.If(satelliteNumber == 'L7', 'SR_B4',
                        ee.Algorithms.If(satelliteNumber == 'L5', 'SR_B4',
                        ee.Algorithms.If(satelliteNumber == 'L4', 'SR_B4')))))

        red = ee.String(ee.Algorithms.If(satelliteNumber == 'L8', 'SR_B4',
                            ee.Algorithms.If(satelliteNumber == 'L7', 'SR_B3',
                            ee.Algorithms.If(satelliteNumber == 'L5', 'SR_B3',
                            ee.Algorithms.If(satelliteNumber == 'L4', 'SR_B3')))))

        # compute NDVI

        NDVI = image.expression('(nir-red)/(nir+red)',{
            'nir' : image.select(nir),
            'red' : image.select(red)
            }).rename('NDVI')
        return image.addBands(NDVI)
    
    return wrap

def AWVhour(image):

    # Landsat Passing Time
    LandsatCenterTime = ee.Date(image.get('system:time_start'))
    date = ee.Date(LandsatCenterTime.format('yyyy-MM-dd'))
    hour = ee.Number.parse(LandsatCenterTime.format('k')).add(ee.Number.parse(LandsatCenterTime.format('m')).divide(60))

    # Load corresponding NCEP AWV data

    # Input acquired date and hour (L8centerTimes), Output AWVhour.
    NCEPdataset = ee.ImageCollection('NCEP_RE/surface_wv').filterDate(date, date.advance(2,'day'))

    totalColumnWaterVapor=NCEPdataset.toBands()
    AWV00 = totalColumnWaterVapor.select(0)
    AWV06 = totalColumnWaterVapor.select(1)
    AWV12 = totalColumnWaterVapor.select(2)
    AWV18 = totalColumnWaterVapor.select(3)
    AWV24 = totalColumnWaterVapor.select(4)

    c1 = ee.Number(ee.Algorithms.If(hour.lt(6), hour,
                       ee.Algorithms.If(hour.lt(12), hour.subtract(6),
                       ee.Algorithms.If(hour.lt(18), hour.subtract(12), hour.subtract(18)))))

    c2 = ee.Number(ee.Algorithms.If(hour.lt(6), ee.Number(6).subtract(hour),
                       ee.Algorithms.If(hour.lt(12), ee.Number(12).subtract(hour),
                       ee.Algorithms.If(hour.lt(18), ee.Number(18).subtract(hour), ee.Number(24).subtract(hour)))))

    AWVhour = ee.Image(ee.Algorithms.If(hour.lt(6), (AWV00.multiply(c2).add(AWV06.multiply(c1))).divide(c1.add(c2)),
                           ee.Algorithms.If(hour.lt(12), (AWV06.multiply(c2).add(AWV12.multiply(c1))).divide(c1.add(c2)),
                           ee.Algorithms.If(hour.lt(18), (AWV12.multiply(c2).add(AWV18.multiply(c1))).divide(c1.add(c2)), (AWV18.multiply(c2).add(AWV24.multiply(c1))).divide(c1.add(c2))))))

    AWVresample = AWVhour.divide(10).resample().rename('AWVhour');    #unit conversion kg/m^2 -> g/cm^2
    
    return image.addBands(AWVresample)  

def EM(satelliteNumber):
    
    def wrap(image):
        ndviSoil = 0.2
        ndviVeg = 0.5
        emissivityWater = 0.995
        emissivityVeg = 0.986
        emissivitySoil = None

        Aster2Landsatc0 = ee.Number(ee.Algorithms.If(satelliteNumber == 'L8', 0.6820,
                                        ee.Algorithms.If(satelliteNumber == 'L7', 0.2147,
                                        ee.Algorithms.If(satelliteNumber == 'L5', -0.0723,
                                        ee.Number(0.3222)))))

        Aster2Landsatc1 = ee.Number(ee.Algorithms.If(satelliteNumber == 'L8', 0.2578,
                                        ee.Algorithms.If(satelliteNumber == 'L7', 0.7789,
                                        ee.Algorithms.If(satelliteNumber == 'L5', 1.0521,
                                        ee.Number(0.6498)))))

        Aster2Landsatc2 = ee.Number(ee.Algorithms.If(satelliteNumber == 'L8', 0.0584,
                                        ee.Algorithms.If(satelliteNumber == 'L7', 0.0058,
                                        ee.Algorithms.If(satelliteNumber == 'L5', 0.0195,
                                        ee.Number(0.0272)))))

        AsterGEDV3 = ee.Image('NASA/ASTER_GED/AG100_003')
        AsterNDVI = AsterGEDV3.select('ndvi').multiply(0.01).clip(image.geometry())
        Aster13Emissivity = AsterGEDV3.select('emissivity_band13').multiply(0.001).clip(image.geometry())
        Aster14Emissivity = AsterGEDV3.select('emissivity_band14').multiply(0.001).clip(image.geometry())

        AsterPV = ee.Image().expression('(asterndvi < ndvisoil)*0 + ((asterndvi >= ndvisoil && asterndvi < ndviveg)*((asterndvi - ndvisoil)/(ndviveg - ndvisoil))**2) + (asterndvi >= ndviveg)*1',{
            'asterndvi' : AsterNDVI,
            'ndvisoil' : ndviSoil,
            'ndviveg' : ndviVeg
        })

        ASTER13emissivitySoil = ee.Image().expression('(asterpv > 0.8)*0.97 + (asterpv < 0.8)*((aster13em - (asterpv*emveg))/(1-asterpv))',{
            'asterpv' : AsterPV,
            'aster13em' : Aster13Emissivity,
            'emveg' : emissivityVeg
        })

        ASTER14emissivitySoil = ee.Image().expression('(asterpv > 0.8)*0.97 + (asterpv < 0.8)*((aster14em - (asterpv*emveg))/(1-asterpv))',{
            'asterpv' : AsterPV,
            'aster14em' : Aster14Emissivity,
            'emveg' : emissivityVeg
        })

        emissivitySoil = ee.Image().expression('(aster13emsoil*c0) + (aster14emsoil*c1) + c2',{
            'aster13emsoil' : ASTER13emissivitySoil,
            'aster14emsoil' : ASTER14emissivitySoil,
            'c0' : Aster2Landsatc0,
            'c1' : Aster2Landsatc1,
            'c2' : Aster2Landsatc2
        })

        emissivitySoil = ee.Image().expression('(emsoil < 0.95)*0.95 + (emsoil >= 0.95)*emsoil',{
            'emsoil' : emissivitySoil
        }).unmask(0.97)

        LandsatPV = ee.Image().expression('(landsatndvi < ndvisoil)*0 + ((landsatndvi >= ndvisoil && landsatndvi < ndviveg)*((landsatndvi-ndvisoil)/(ndviveg-ndvisoil))**2) + (landsatndvi >= ndviveg)*1',{
            'landsatndvi' : image.select('NDVI'),
            'ndvisoil' : ndviSoil,
            'ndviveg' : ndviVeg
        }).rename('FVC')

        LandsatEmissivity = ee.Image().expression('(landsatndvi < 0)*emwater + (landsatndvi >= 0 && landsatndvi < ndvisoil)*emsoil + ((landsatndvi >= ndvisoil && landsatndvi < ndviveg)*(landsatpv * emveg + (1 - landsatpv)*emsoil)) + (landsatndvi >= ndviveg)*emveg', {
            'landsatndvi' : image.select('NDVI'),
            'emwater' : emissivityWater,
            'ndvisoil' : ndviSoil,
            'ndviveg' : ndviVeg,
            'emsoil' : emissivitySoil,
            'emveg' : emissivityVeg,
            'landsatpv' : LandsatPV
        }).rename('Emissivity')
        return image.addBands(LandsatEmissivity) \
                    .addBands(LandsatPV)
    return wrap
    

def LST(satelliteNumber):
    
    def wrap(image):
        effWavelenght = ee.Number(ee.Algorithms.If(satelliteNumber == 'L8', 10.904,
                                  ee.Algorithms.If(satelliteNumber == 'L7', 11.269,
                                  ee.Algorithms.If(satelliteNumber == 'L5', 11.457,
                                  ee.Algorithms.If(satelliteNumber == 'L4', 11.154)))))

        PSCcoefficients = ee.List(ee.Algorithms.If(satelliteNumber == 'L8', [-0.4107, 1.493577, 0.278271, -1.22502, -0.31067, 1.022016, -0.01969, 0.036001],
                                      ee.Algorithms.If(satelliteNumber == 'L7', [-0.383841, 1.572869, 0.261657, -1.462534, -0.279104, 1.024070, 0.000557, 0.033393],
                                      ee.Algorithms.If(satelliteNumber == 'L5', [-0.374535, 1.615873, 0.249358, -1.540580, -0.280461, 1.026033, 0.004315, 0.034258],
                                      ee.Algorithms.If(satelliteNumber == 'L4', [-0.400985, 1.563747, 0.282200, -1.430355, -0.276741, 1.022396, -0.002946, 0.032781])))))

        ThermalRadiance = ee.Image(ee.Algorithms.If(satelliteNumber == 'L8', image.select('B10'),
                                       ee.Algorithms.If(satelliteNumber == 'L7', image.select('B6_VCID_1'),
                                       ee.Algorithms.If(satelliteNumber == 'L5', image.select('B6'),
                                       ee.Algorithms.If(satelliteNumber == 'L4', image.select('B6'))))))

        LeavingSurfaceRad = ee.Image().expression('a0 + (a1*w) + (((a2+(a3*w)+(a4*(w**2))))/em) + ((a5+(a6*w)+(a7*(w**2)))*(thermalradiance/em))',{
            'a0' : ee.Number(PSCcoefficients.get(0)),
            'a1' : ee.Number(PSCcoefficients.get(1)),
            'a2' : ee.Number(PSCcoefficients.get(2)),
            'a3' : ee.Number(PSCcoefficients.get(3)),
            'a4' : ee.Number(PSCcoefficients.get(4)),
            'a5' : ee.Number(PSCcoefficients.get(5)),
            'a6' : ee.Number(PSCcoefficients.get(6)),
            'a7' : ee.Number(PSCcoefficients.get(7)),
            'w' : image.select('AWVhour'),
            'em' :image.select('Emissivity'),
            'thermalradiance' : ThermalRadiance
        })

        LST = ee.Image().expression('(c2/effwavelenght)/log((c1/(effwavelenght**5 * leavingsurfrad))+1)',{
            'c2' : 14387.7,
            'c1' : 119104000,
            'effwavelenght' : effWavelenght,
            'leavingsurfrad' : LeavingSurfaceRad

        }).rename('LST').subtract(273.15)
        
        return image.addBands(LST)
    return wrap

def LandsatLSTretrieval(satelliteNumber, date_start, date_end, geometry):
    
    LandsatRawCollection = ee.ImageCollection(ee.Algorithms.If(satelliteNumber == 'L8', ee.ImageCollection("LANDSAT/LC08/C02/T1"),
                                                  ee.Algorithms.If(satelliteNumber == 'L7', ee.ImageCollection("LANDSAT/LE07/C02/T1"),
                                                  ee.Algorithms.If(satelliteNumber == 'L5', ee.ImageCollection("LANDSAT/LT05/C02/T1"),
                                                  ee.Algorithms.If(satelliteNumber == 'L4', ee.ImageCollection("LANDSAT/LT04/C02/T1"))))))

    LandsatSurfaceCollection = ee.ImageCollection(ee.Algorithms.If(satelliteNumber == 'L8', ee.ImageCollection("LANDSAT/LC08/C02/T1_L2"),
                                                      ee.Algorithms.If(satelliteNumber == 'L7', ee.ImageCollection("LANDSAT/LE07/C02/T1_L2"),
                                                      ee.Algorithms.If(satelliteNumber == 'L5', ee.ImageCollection("LANDSAT/LT05/C02/T1_L2"),
                                                      ee.Algorithms.If(satelliteNumber == 'L4', ee.ImageCollection("LANDSAT/LT04/C02/T1_L2"))))))

    LandsatRawImage = LandsatRawCollection.filterDate(date_start, date_end) \
                                              .filterBounds(geometry) \
                                              .map(mask) \
                                              .map(lambda image:ee.Algorithms.Landsat.calibratedRadiance(image))

    LandsatSurfaceImage = LandsatSurfaceCollection.filterDate(date_start, date_end) \
                                                      .filterBounds(geometry) \
                                                      .map(mask) \
                                                      .map(SR) \
                                                      .map(AWVhour) \
                                                      .map(ndvi(satelliteNumber)) \
                                                      .map(EM(satelliteNumber))

    tir = ee.Algorithms.If(satelliteNumber == 'L8', ['B10','B11'],
              ee.Algorithms.If(satelliteNumber == 'L7', ['B6_VCID_1','B6_VCID_2'],
              ee.Algorithms.If(satelliteNumber == 'L5', ['B6'],
              ee.Algorithms.If(satelliteNumber == 'L4', ['B6']))))

    LandsatAll = LandsatSurfaceImage.combine(LandsatRawImage.select(tir))

    landsatLST = LandsatAll.map(LST(satelliteNumber))
    
    return landsatLST
