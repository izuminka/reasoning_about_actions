(define (problem strips-sat-x-1)
(:domain satellite)
(:objects
	satellite0 - satellite
	instrument0 - instrument
	instrument1 - instrument
	instrument2 - instrument
	satellite1 - satellite
	instrument3 - instrument
	image3 - mode
	infrared1 - mode
	image2 - mode
	image0 - mode
	GroundStation2 - direction
	GroundStation3 - direction
	GroundStation4 - direction
	Star1 - direction
	GroundStation0 - direction
	GroundStation7 - direction
	Star9 - direction
	GroundStation5 - direction
	Star6 - direction
	Star8 - direction
	Phenomenon10 - direction
	Planet11 - direction
	Planet12 - direction
	Planet13 - direction
	Planet14 - direction
	Star15 - direction
	Phenomenon16 - direction
	Phenomenon17 - direction
)
(:init
	(supports instrument0 image3)
	(supports instrument0 infrared1)
	(calibration_target instrument0 Star9)
	(calibration_target instrument0 Star1)
	(supports instrument1 image3)
	(supports instrument1 image0)
	(supports instrument1 infrared1)
	(calibration_target instrument1 GroundStation0)
	(supports instrument2 image3)
	(supports instrument2 image2)
	(calibration_target instrument2 Star9)
	(calibration_target instrument2 GroundStation5)
	(calibration_target instrument2 GroundStation7)
	(on_board instrument0 satellite0)
	(on_board instrument1 satellite0)
	(on_board instrument2 satellite0)
	(power_avail satellite0)
	(pointing satellite0 GroundStation3)
	(supports instrument3 image3)
	(supports instrument3 image2)
	(supports instrument3 image0)
	(calibration_target instrument3 Star8)
	(calibration_target instrument3 Star6)
	(calibration_target instrument3 GroundStation5)
	(on_board instrument3 satellite1)
	(power_avail satellite1)
	(pointing satellite1 Phenomenon10)
)
(:goal (and
	(pointing satellite0 GroundStation3)
	(pointing satellite1 Star15)
	(have_image Phenomenon10 infrared1)
	(have_image Planet11 image3)
	(have_image Planet12 infrared1)
	(have_image Planet13 image0)
	(have_image Planet14 image0)
	(have_image Star15 image2)
	(have_image Phenomenon16 image3)
	(have_image Phenomenon17 image3)
))

)
