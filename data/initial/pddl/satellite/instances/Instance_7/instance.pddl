(define (problem strips-sat-x-1)
(:domain satellite)
(:objects
	satellite0 - satellite
	instrument0 - instrument
	instrument1 - instrument
	satellite1 - satellite
	instrument2 - instrument
	satellite2 - satellite
	instrument3 - instrument
	instrument4 - instrument
	instrument5 - instrument
	thermograph2 - mode
	spectrograph3 - mode
	image1 - mode
	infrared0 - mode
	Star0 - direction
	Star1 - direction
	Star2 - direction
	Star3 - direction
	Phenomenon4 - direction
	Star5 - direction
	Planet6 - direction
	Star7 - direction
)
(:init
	(supports instrument0 infrared0)
	(supports instrument0 thermograph2)
	(calibration_target instrument0 Star0)
	(supports instrument1 thermograph2)
	(supports instrument1 spectrograph3)
	(calibration_target instrument1 Star0)
	(on_board instrument0 satellite0)
	(on_board instrument1 satellite0)
	(power_avail satellite0)
	(pointing satellite0 Phenomenon4)
	(supports instrument2 thermograph2)
	(calibration_target instrument2 Star0)
	(on_board instrument2 satellite1)
	(power_avail satellite1)
	(pointing satellite1 Planet6)
	(supports instrument3 image1)
	(supports instrument3 thermograph2)
	(supports instrument3 infrared0)
	(calibration_target instrument3 Star0)
	(supports instrument4 infrared0)
	(supports instrument4 thermograph2)
	(supports instrument4 image1)
	(calibration_target instrument4 Star0)
	(supports instrument5 thermograph2)
	(supports instrument5 image1)
	(supports instrument5 infrared0)
	(calibration_target instrument5 Star0)
	(on_board instrument3 satellite2)
	(on_board instrument4 satellite2)
	(on_board instrument5 satellite2)
	(power_avail satellite2)
	(pointing satellite2 Star3)
)
(:goal (and
	(pointing satellite1 Star3)
	(pointing satellite2 Star2)
	(have_image Star1 spectrograph3)
	(have_image Star2 spectrograph3)
	(have_image Star3 image1)
	(have_image Phenomenon4 image1)
	(have_image Star5 image1)
	(have_image Planet6 image1)
	(have_image Star7 image1)
))

)
