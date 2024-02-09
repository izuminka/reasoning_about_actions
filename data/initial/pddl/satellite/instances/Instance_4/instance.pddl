(define (problem strips-sat-x-1)
(:domain satellite)
(:objects
	satellite0 - satellite
	instrument0 - instrument
	satellite1 - satellite
	instrument1 - instrument
	image2 - mode
	spectrograph1 - mode
	image4 - mode
	spectrograph3 - mode
	image5 - mode
	image0 - mode
	GroundStation0 - direction
	GroundStation2 - direction
	Star3 - direction
	GroundStation4 - direction
	Star1 - direction
	Phenomenon5 - direction
	Star6 - direction
	Phenomenon7 - direction
	Planet8 - direction
	Phenomenon9 - direction
	Phenomenon10 - direction
	Phenomenon11 - direction
)
(:init
	(supports instrument0 image2)
	(calibration_target instrument0 Star1)
	(on_board instrument0 satellite0)
	(power_avail satellite0)
	(pointing satellite0 Phenomenon5)
	(supports instrument1 image2)
	(supports instrument1 image0)
	(supports instrument1 image4)
	(supports instrument1 image5)
	(supports instrument1 spectrograph3)
	(supports instrument1 spectrograph1)
	(calibration_target instrument1 Star1)
	(on_board instrument1 satellite1)
	(power_avail satellite1)
	(pointing satellite1 Star3)
)
(:goal (and
	(pointing satellite0 Star6)
	(have_image Phenomenon5 image4)
	(have_image Phenomenon5 image5)
	(have_image Star6 image4)
	(have_image Phenomenon7 image0)
	(have_image Phenomenon7 image4)
	(have_image Planet8 image5)
	(have_image Phenomenon9 image5)
	(have_image Phenomenon9 spectrograph1)
	(have_image Phenomenon10 image5)
	(have_image Phenomenon10 spectrograph3)
	(have_image Phenomenon11 spectrograph1)
))

)
