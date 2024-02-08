(define (problem strips-sat-x-1)
(:domain satellite)
(:objects
	satellite0 - satellite
	instrument0 - instrument
	satellite1 - satellite
	instrument1 - instrument
	instrument2 - instrument
	instrument3 - instrument
	satellite2 - satellite
	instrument4 - instrument
	instrument5 - instrument
	satellite3 - satellite
	instrument6 - instrument
	instrument7 - instrument
	satellite4 - satellite
	instrument8 - instrument
	instrument9 - instrument
	satellite5 - satellite
	instrument10 - instrument
	instrument11 - instrument
	instrument12 - instrument
	satellite6 - satellite
	instrument13 - instrument
	satellite7 - satellite
	instrument14 - instrument
	spectrograph5 - mode
	spectrograph2 - mode
	image7 - mode
	infrared3 - mode
	image1 - mode
	image0 - mode
	thermograph6 - mode
	infrared4 - mode
	GroundStation0 - direction
	Star1 - direction
	Planet2 - direction
	Phenomenon3 - direction
)
(:init
	(supports instrument0 infrared4)
	(supports instrument0 image7)
	(supports instrument0 image1)
	(calibration_target instrument0 GroundStation0)
	(on_board instrument0 satellite0)
	(power_avail satellite0)
	(pointing satellite0 GroundStation0)
	(supports instrument1 spectrograph5)
	(supports instrument1 infrared3)
	(supports instrument1 thermograph6)
	(calibration_target instrument1 GroundStation0)
	(supports instrument2 infrared4)
	(supports instrument2 infrared3)
	(calibration_target instrument2 GroundStation0)
	(supports instrument3 spectrograph2)
	(supports instrument3 thermograph6)
	(calibration_target instrument3 GroundStation0)
	(on_board instrument1 satellite1)
	(on_board instrument2 satellite1)
	(on_board instrument3 satellite1)
	(power_avail satellite1)
	(pointing satellite1 GroundStation0)
	(supports instrument4 image0)
	(calibration_target instrument4 GroundStation0)
	(supports instrument5 spectrograph5)
	(supports instrument5 spectrograph2)
	(supports instrument5 image0)
	(calibration_target instrument5 GroundStation0)
	(on_board instrument4 satellite2)
	(on_board instrument5 satellite2)
	(power_avail satellite2)
	(pointing satellite2 GroundStation0)
	(supports instrument6 thermograph6)
	(calibration_target instrument6 GroundStation0)
	(supports instrument7 image7)
	(calibration_target instrument7 GroundStation0)
	(on_board instrument6 satellite3)
	(on_board instrument7 satellite3)
	(power_avail satellite3)
	(pointing satellite3 Phenomenon3)
	(supports instrument8 image7)
	(supports instrument8 infrared3)
	(calibration_target instrument8 GroundStation0)
	(supports instrument9 infrared4)
	(calibration_target instrument9 GroundStation0)
	(on_board instrument8 satellite4)
	(on_board instrument9 satellite4)
	(power_avail satellite4)
	(pointing satellite4 Phenomenon3)
	(supports instrument10 infrared3)
	(supports instrument10 thermograph6)
	(calibration_target instrument10 GroundStation0)
	(supports instrument11 image1)
	(calibration_target instrument11 GroundStation0)
	(supports instrument12 image0)
	(supports instrument12 spectrograph5)
	(supports instrument12 image1)
	(calibration_target instrument12 GroundStation0)
	(on_board instrument10 satellite5)
	(on_board instrument11 satellite5)
	(on_board instrument12 satellite5)
	(power_avail satellite5)
	(pointing satellite5 GroundStation0)
	(supports instrument13 infrared3)
	(supports instrument13 infrared4)
	(calibration_target instrument13 GroundStation0)
	(on_board instrument13 satellite6)
	(power_avail satellite6)
	(pointing satellite6 Phenomenon3)
	(supports instrument14 infrared3)
	(supports instrument14 infrared4)
	(supports instrument14 spectrograph5)
	(calibration_target instrument14 GroundStation0)
	(on_board instrument14 satellite7)
	(power_avail satellite7)
	(pointing satellite7 Phenomenon3)
)
(:goal (and
	(pointing satellite0 Star1)
	(pointing satellite2 Star1)
	(pointing satellite5 Planet2)
	(have_image Star1 thermograph6)
	(have_image Planet2 image0)
	(have_image Phenomenon3 spectrograph2)
))

)
