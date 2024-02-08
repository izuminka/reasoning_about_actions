(define (problem strips-sat-x-1)
(:domain satellite)
(:objects
	satellite0 - satellite
	instrument0 - instrument
	instrument1 - instrument
	instrument2 - instrument
	instrument3 - instrument
	instrument4 - instrument
	satellite1 - satellite
	instrument5 - instrument
	instrument6 - instrument
	instrument7 - instrument
	satellite2 - satellite
	instrument8 - instrument
	instrument9 - instrument
	instrument10 - instrument
	instrument11 - instrument
	instrument12 - instrument
	satellite3 - satellite
	instrument13 - instrument
	instrument14 - instrument
	instrument15 - instrument
	instrument16 - instrument
	satellite4 - satellite
	instrument17 - instrument
	instrument18 - instrument
	instrument19 - instrument
	instrument20 - instrument
	instrument21 - instrument
	instrument22 - instrument
	spectrograph3 - mode
	spectrograph1 - mode
	image0 - mode
	infrared4 - mode
	infrared2 - mode
	GroundStation2 - direction
	Star0 - direction
	GroundStation4 - direction
	GroundStation1 - direction
	GroundStation3 - direction
	Planet5 - direction
)
(:init
	(supports instrument0 infrared2)
	(supports instrument0 image0)
	(calibration_target instrument0 Star0)
	(supports instrument1 spectrograph1)
	(supports instrument1 image0)
	(supports instrument1 infrared4)
	(calibration_target instrument1 GroundStation1)
	(supports instrument2 infrared4)
	(supports instrument2 spectrograph1)
	(calibration_target instrument2 Star0)
	(supports instrument3 infrared4)
	(supports instrument3 infrared2)
	(supports instrument3 spectrograph1)
	(calibration_target instrument3 GroundStation2)
	(supports instrument4 image0)
	(supports instrument4 spectrograph3)
	(calibration_target instrument4 GroundStation3)
	(on_board instrument0 satellite0)
	(on_board instrument1 satellite0)
	(on_board instrument2 satellite0)
	(on_board instrument3 satellite0)
	(on_board instrument4 satellite0)
	(power_avail satellite0)
	(pointing satellite0 GroundStation3)
	(supports instrument5 spectrograph3)
	(supports instrument5 image0)
	(supports instrument5 infrared4)
	(calibration_target instrument5 Star0)
	(supports instrument6 spectrograph3)
	(calibration_target instrument6 GroundStation1)
	(supports instrument7 image0)
	(supports instrument7 spectrograph3)
	(supports instrument7 spectrograph1)
	(calibration_target instrument7 GroundStation3)
	(on_board instrument5 satellite1)
	(on_board instrument6 satellite1)
	(on_board instrument7 satellite1)
	(power_avail satellite1)
	(pointing satellite1 GroundStation1)
	(supports instrument8 spectrograph3)
	(supports instrument8 image0)
	(calibration_target instrument8 GroundStation4)
	(supports instrument9 spectrograph3)
	(calibration_target instrument9 GroundStation1)
	(supports instrument10 spectrograph1)
	(supports instrument10 infrared2)
	(supports instrument10 infrared4)
	(calibration_target instrument10 GroundStation1)
	(supports instrument11 infrared2)
	(supports instrument11 image0)
	(calibration_target instrument11 Star0)
	(supports instrument12 infrared2)
	(supports instrument12 infrared4)
	(supports instrument12 spectrograph3)
	(calibration_target instrument12 GroundStation2)
	(on_board instrument8 satellite2)
	(on_board instrument9 satellite2)
	(on_board instrument10 satellite2)
	(on_board instrument11 satellite2)
	(on_board instrument12 satellite2)
	(power_avail satellite2)
	(pointing satellite2 GroundStation1)
	(supports instrument13 infrared2)
	(supports instrument13 infrared4)
	(calibration_target instrument13 GroundStation2)
	(supports instrument14 infrared2)
	(supports instrument14 image0)
	(supports instrument14 infrared4)
	(calibration_target instrument14 GroundStation2)
	(supports instrument15 infrared4)
	(supports instrument15 infrared2)
	(supports instrument15 spectrograph3)
	(calibration_target instrument15 GroundStation2)
	(supports instrument16 image0)
	(supports instrument16 infrared4)
	(supports instrument16 spectrograph3)
	(calibration_target instrument16 GroundStation1)
	(on_board instrument13 satellite3)
	(on_board instrument14 satellite3)
	(on_board instrument15 satellite3)
	(on_board instrument16 satellite3)
	(power_avail satellite3)
	(pointing satellite3 Star0)
	(supports instrument17 spectrograph1)
	(supports instrument17 infrared2)
	(supports instrument17 image0)
	(calibration_target instrument17 Star0)
	(supports instrument18 image0)
	(calibration_target instrument18 GroundStation3)
	(supports instrument19 infrared2)
	(supports instrument19 infrared4)
	(calibration_target instrument19 GroundStation4)
	(supports instrument20 infrared2)
	(supports instrument20 image0)
	(supports instrument20 infrared4)
	(calibration_target instrument20 GroundStation3)
	(supports instrument21 infrared2)
	(supports instrument21 spectrograph3)
	(calibration_target instrument21 GroundStation1)
	(supports instrument22 image0)
	(calibration_target instrument22 GroundStation3)
	(on_board instrument17 satellite4)
	(on_board instrument18 satellite4)
	(on_board instrument19 satellite4)
	(on_board instrument20 satellite4)
	(on_board instrument21 satellite4)
	(on_board instrument22 satellite4)
	(power_avail satellite4)
	(pointing satellite4 GroundStation4)
)
(:goal (and
	(pointing satellite1 GroundStation3)
	(pointing satellite2 Planet5)
	(have_image Planet5 spectrograph1)
))

)
