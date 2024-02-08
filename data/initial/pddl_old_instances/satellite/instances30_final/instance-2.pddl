(define (problem strips-sat-x-1)
(:domain satellite)
(:objects
	satellite0 - satellite
	instrument0 - instrument
	instrument1 - instrument
	instrument2 - instrument
	satellite1 - satellite
	instrument3 - instrument
	instrument4 - instrument
	instrument5 - instrument
	instrument6 - instrument
	instrument7 - instrument
	instrument8 - instrument
	satellite2 - satellite
	instrument9 - instrument
	instrument10 - instrument
	instrument11 - instrument
	instrument12 - instrument
	instrument13 - instrument
	image4 - mode
	thermograph2 - mode
	thermograph6 - mode
	image0 - mode
	thermograph3 - mode
	thermograph1 - mode
	image5 - mode
	GroundStation1 - direction
	GroundStation6 - direction
	Star5 - direction
	GroundStation3 - direction
	Star7 - direction
	GroundStation0 - direction
	GroundStation2 - direction
	Star4 - direction
	Phenomenon8 - direction
	Phenomenon9 - direction
)
(:init
	(supports instrument0 image4)
	(calibration_target instrument0 GroundStation0)
	(supports instrument1 thermograph6)
	(calibration_target instrument1 GroundStation6)
	(calibration_target instrument1 Star4)
	(supports instrument2 thermograph3)
	(calibration_target instrument2 Star7)
	(calibration_target instrument2 GroundStation2)
	(on_board instrument0 satellite0)
	(on_board instrument1 satellite0)
	(on_board instrument2 satellite0)
	(power_avail satellite0)
	(pointing satellite0 GroundStation2)
	(supports instrument3 thermograph2)
	(supports instrument3 image4)
	(supports instrument3 thermograph3)
	(calibration_target instrument3 Star7)
	(calibration_target instrument3 Star4)
	(supports instrument4 image0)
	(supports instrument4 image4)
	(calibration_target instrument4 Star4)
	(supports instrument5 image5)
	(calibration_target instrument5 GroundStation2)
	(supports instrument6 image5)
	(supports instrument6 thermograph3)
	(supports instrument6 thermograph1)
	(calibration_target instrument6 GroundStation3)
	(calibration_target instrument6 Star4)
	(supports instrument7 image5)
	(supports instrument7 image4)
	(supports instrument7 thermograph2)
	(calibration_target instrument7 GroundStation0)
	(supports instrument8 image5)
	(supports instrument8 thermograph6)
	(calibration_target instrument8 Star5)
	(on_board instrument3 satellite1)
	(on_board instrument4 satellite1)
	(on_board instrument5 satellite1)
	(on_board instrument6 satellite1)
	(on_board instrument7 satellite1)
	(on_board instrument8 satellite1)
	(power_avail satellite1)
	(pointing satellite1 GroundStation2)
	(supports instrument9 thermograph3)
	(supports instrument9 image4)
	(calibration_target instrument9 GroundStation3)
	(supports instrument10 thermograph3)
	(calibration_target instrument10 Star7)
	(calibration_target instrument10 GroundStation0)
	(supports instrument11 image4)
	(calibration_target instrument11 GroundStation2)
	(calibration_target instrument11 GroundStation0)
	(supports instrument12 thermograph1)
	(supports instrument12 thermograph6)
	(supports instrument12 image0)
	(calibration_target instrument12 GroundStation2)
	(supports instrument13 thermograph6)
	(supports instrument13 image5)
	(calibration_target instrument13 Star4)
	(on_board instrument9 satellite2)
	(on_board instrument10 satellite2)
	(on_board instrument11 satellite2)
	(on_board instrument12 satellite2)
	(on_board instrument13 satellite2)
	(power_avail satellite2)
	(pointing satellite2 Star4)
)
(:goal (and
	(pointing satellite1 GroundStation0)
	(have_image Phenomenon8 image4)
	(have_image Phenomenon9 thermograph6)
))

)
