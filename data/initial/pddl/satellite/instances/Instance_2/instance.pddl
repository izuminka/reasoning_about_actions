(define (problem strips-sat-x-1)
(:domain satellite)
(:objects
	satellite0 - satellite
	instrument0 - instrument
	instrument1 - instrument
	instrument2 - instrument
	instrument3 - instrument
	satellite1 - satellite
	instrument4 - instrument
	thermograph3 - mode
	image6 - mode
	image5 - mode
	spectrograph2 - mode
	image0 - mode
	image1 - mode
	infrared7 - mode
	spectrograph4 - mode
	GroundStation1 - direction
	GroundStation2 - direction
	GroundStation5 - direction
	GroundStation7 - direction
	Star3 - direction
	GroundStation6 - direction
	GroundStation0 - direction
	Star4 - direction
	GroundStation9 - direction
	GroundStation8 - direction
	Star10 - direction
	Planet11 - direction
	Star12 - direction
	Planet13 - direction
	Phenomenon14 - direction
	Phenomenon15 - direction
	Star16 - direction
)
(:init
	(supports instrument0 image6)
	(calibration_target instrument0 Star3)
	(calibration_target instrument0 GroundStation7)
	(supports instrument1 spectrograph2)
	(supports instrument1 image6)
	(supports instrument1 image5)
	(calibration_target instrument1 GroundStation0)
	(calibration_target instrument1 GroundStation6)
	(supports instrument2 image1)
	(supports instrument2 image0)
	(calibration_target instrument2 Star4)
	(supports instrument3 image1)
	(supports instrument3 thermograph3)
	(supports instrument3 spectrograph4)
	(calibration_target instrument3 GroundStation9)
	(on_board instrument0 satellite0)
	(on_board instrument1 satellite0)
	(on_board instrument2 satellite0)
	(on_board instrument3 satellite0)
	(power_avail satellite0)
	(pointing satellite0 GroundStation2)
	(supports instrument4 infrared7)
	(supports instrument4 image1)
	(calibration_target instrument4 GroundStation8)
	(on_board instrument4 satellite1)
	(power_avail satellite1)
	(pointing satellite1 Planet13)
)
(:goal (and
	(have_image Star10 image6)
	(have_image Star10 spectrograph2)
	(have_image Planet11 image5)
	(have_image Planet11 image6)
	(have_image Star12 spectrograph4)
	(have_image Planet13 image5)
	(have_image Planet13 spectrograph2)
	(have_image Phenomenon14 thermograph3)
	(have_image Phenomenon14 spectrograph4)
	(have_image Phenomenon15 spectrograph4)
	(have_image Star16 image0)
))

)
