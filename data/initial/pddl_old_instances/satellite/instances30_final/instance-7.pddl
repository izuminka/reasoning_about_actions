(define (problem strips-sat-x-1)
(:domain satellite)
(:objects
	satellite0 - satellite
	instrument0 - instrument
	instrument1 - instrument
	instrument2 - instrument
	instrument3 - instrument
	image1 - mode
	thermograph4 - mode
	image0 - mode
	image2 - mode
	spectrograph6 - mode
	thermograph3 - mode
	infrared5 - mode
	Star0 - direction
	Planet1 - direction
	Phenomenon2 - direction
)
(:init
	(supports instrument0 infrared5)
	(supports instrument0 image1)
	(calibration_target instrument0 Star0)
	(supports instrument1 spectrograph6)
	(supports instrument1 thermograph4)
	(calibration_target instrument1 Star0)
	(supports instrument2 image1)
	(supports instrument2 image2)
	(calibration_target instrument2 Star0)
	(supports instrument3 infrared5)
	(supports instrument3 thermograph3)
	(supports instrument3 image0)
	(calibration_target instrument3 Star0)
	(on_board instrument0 satellite0)
	(on_board instrument1 satellite0)
	(on_board instrument2 satellite0)
	(on_board instrument3 satellite0)
	(power_avail satellite0)
	(pointing satellite0 Phenomenon2)
)
(:goal (and
	(have_image Planet1 thermograph4)
	(have_image Phenomenon2 thermograph4)
))

)
