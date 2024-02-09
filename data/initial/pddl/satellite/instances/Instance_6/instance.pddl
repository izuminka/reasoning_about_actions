(define (problem strips-sat-x-1)
(:domain satellite)
(:objects
	satellite0 - satellite
	instrument0 - instrument
	instrument1 - instrument
	satellite1 - satellite
	instrument2 - instrument
	instrument3 - instrument
	satellite2 - satellite
	instrument4 - instrument
	instrument5 - instrument
	infrared5 - mode
	spectrograph3 - mode
	image1 - mode
	thermograph0 - mode
	infrared4 - mode
	thermograph2 - mode
	Star3 - direction
	GroundStation0 - direction
	Star2 - direction
	Star1 - direction
	Phenomenon4 - direction
	Planet5 - direction
	Planet6 - direction
	Star7 - direction
	Star8 - direction
)
(:init
	(supports instrument0 thermograph0)
	(supports instrument0 spectrograph3)
	(calibration_target instrument0 Star3)
	(supports instrument1 infrared4)
	(supports instrument1 image1)
	(supports instrument1 infrared5)
	(supports instrument1 thermograph2)
	(calibration_target instrument1 GroundStation0)
	(on_board instrument0 satellite0)
	(on_board instrument1 satellite0)
	(power_avail satellite0)
	(pointing satellite0 Star7)
	(supports instrument2 thermograph0)
	(supports instrument2 spectrograph3)
	(calibration_target instrument2 Star2)
	(supports instrument3 image1)
	(calibration_target instrument3 Star1)
	(on_board instrument2 satellite1)
	(on_board instrument3 satellite1)
	(power_avail satellite1)
	(pointing satellite1 Star8)
	(supports instrument4 spectrograph3)
	(calibration_target instrument4 Star2)
	(supports instrument5 thermograph0)
	(calibration_target instrument5 Star1)
	(on_board instrument4 satellite2)
	(on_board instrument5 satellite2)
	(power_avail satellite2)
	(pointing satellite2 Star2)
)
(:goal (and
	(have_image Phenomenon4 thermograph2)
	(have_image Planet5 image1)
	(have_image Planet6 image1)
	(have_image Planet6 thermograph0)
	(have_image Star7 infrared4)
	(have_image Star7 spectrograph3)
	(have_image Star8 spectrograph3)
))

)
