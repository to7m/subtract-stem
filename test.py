from subtract_stem_lib import *


load_audio()
save_audio()
safe_reciprocal__c()
safe_divide__cf()
for x in GenerateSpectra(logger=True):
    print(x)
for x in GenerateStemAndMixSpectra(logger=True):
    print(x)
x = GenerateSingleEqProfile(logger=True).run()
for x in GenerateRunningEqProfile(logger=True):
    print(x)
find_delay_stem_s(logger=True)
subtract_single_stem_from_mix(logger=True)
subtract_running_stem_from_mix(logger=True)
subtract_single_intermediate_from_mix(logger=True)
subtract_running_intermediate_from_mix(logger=True)
