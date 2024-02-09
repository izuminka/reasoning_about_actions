(define (problem strips-sat-x-1)
(:domain satellite)
(:objects
	satellite0 - satellite
	instrument0 - instrument
	satellite1 - satellite
	instrument1 - instrument
	satellite2 - satellite
	instrument2 - instrument
	instrument3 - instrument
	image2 - mode
	spectrograph0 - mode
	spectrograph3 - mode
	infrared5 - mode
	image4 - mode
	thermograph1 - mode
	GroundStation3 - direction
	GroundStation0 - direction
	GroundStation2 - direction
	Star5 - direction
	Star4 - direction
	Star1 - direction
	Star6 - direction
	Star7 - direction
	Phenomenon8 - direction
	Phenomenon9 - direction
	Planet10 - direction
	Star11 - direction
)
(:init
	(supports instrument0 image2)
	(supports instrument0 infrared5)
	(supports instrument0 thermograph1)
	(calibration_target instrument0 GroundStation2)
	(calibration_target instrument0 GroundStation3)
	(on_board instrument0 satellite0)
	(power_avail satellite0)
	(pointing satellite0 Planet10)
	(supports instrument1 spectrograph3)
	(calibration_target instrument1 GroundStation2)
	(calibration_target instrument1 GroundStation0)
	(on_board instrument1 satellite1)
	(power_avail satellite1)
	(pointing satellite1 Star5)
	(supports instrument2 image4)
	(supports instrument2 spectrograph0)
	(calibration_target instrument2 Star5)
	(supports instrument3 image4)
	(supports instrument3 image2)
	(calibration_target instrument3 Star1)
	(calibration_target instrument3 Star4)
	(on_board instrument2 satellite2)
	(on_board instrument3 satellite2)
	(power_avail satellite2)
	(pointing satellite2 Phenomenon8)
)
(:goal (and
	(pointing satellite0 Star5)
	(have_image Star6 spectrograph0)
	(have_image Star6 thermograph1)
	(have_image Star7 image2)
	(have_image Star7 thermograph1)
	(have_image Phenomenon8 image4)
	(have_image Phenomenon9 image2)
	(have_image Phenomenon9 thermograph1)
	(have_image Planet10 spectrograph0)
	(have_image Star11 thermograph1)
))

)
