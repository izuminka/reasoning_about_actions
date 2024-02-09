(define (problem strips-sat-x-1)
(:domain satellite)
(:objects
	satellite0 - satellite
	instrument0 - instrument
	satellite1 - satellite
	instrument1 - instrument
	instrument2 - instrument
	satellite2 - satellite
	instrument3 - instrument
	instrument4 - instrument
	infrared0 - mode
	infrared2 - mode
	thermograph4 - mode
	image3 - mode
	spectrograph1 - mode
	GroundStation1 - direction
	GroundStation2 - direction
	Star3 - direction
	Star4 - direction
	GroundStation6 - direction
	GroundStation5 - direction
	Star0 - direction
	GroundStation7 - direction
	Star8 - direction
	Planet9 - direction
	Star10 - direction
	Star11 - direction
	Planet12 - direction
	Star13 - direction
)
(:init
	(supports instrument0 image3)
	(supports instrument0 thermograph4)
	(supports instrument0 infrared2)
	(calibration_target instrument0 Star0)
	(calibration_target instrument0 GroundStation5)
	(on_board instrument0 satellite0)
	(power_avail satellite0)
	(pointing satellite0 GroundStation6)
	(supports instrument1 thermograph4)
	(calibration_target instrument1 GroundStation7)
	(calibration_target instrument1 Star0)
	(supports instrument2 spectrograph1)
	(supports instrument2 thermograph4)
	(calibration_target instrument2 GroundStation5)
	(calibration_target instrument2 Star0)
	(on_board instrument1 satellite1)
	(on_board instrument2 satellite1)
	(power_avail satellite1)
	(pointing satellite1 Star11)
	(supports instrument3 thermograph4)
	(calibration_target instrument3 Star0)
	(supports instrument4 thermograph4)
	(supports instrument4 infrared0)
	(calibration_target instrument4 GroundStation7)
	(on_board instrument3 satellite2)
	(on_board instrument4 satellite2)
	(power_avail satellite2)
	(pointing satellite2 Star10)
)
(:goal (and
	(pointing satellite1 Star0)
	(pointing satellite2 Planet12)
	(have_image Star8 infrared0)
	(have_image Planet9 infrared0)
	(have_image Star10 spectrograph1)
	(have_image Star11 infrared0)
	(have_image Planet12 thermograph4)
	(have_image Star13 image3)
))

)
