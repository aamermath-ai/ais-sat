/* Omega Worksheets catalogue: grade → term → module → worksheet.
   Used by worksheets.html (the list students see) and teacher.html (the "Assign" picker).
   To add a worksheet: put its HTML file in source/worksheets/, add an item here, then run python3 source/build.py.
   "ws" must match the id in the worksheet's window.AISWS, so teachers can assign it to a class. */
const GRADES=[
  {id:"6",name:"Grade 6",course:"Mathematics",terms:[]},
  {id:"7",name:"Grade 7",course:"Mathematics",terms:[]},
  {id:"8",name:"Grade 8",course:"Mathematics",terms:[]},
  {id:"9",name:"Grade 9",course:"Algebra 1",terms:[
    {name:"Term 1",modules:[
      {name:"Module 2",topic:"Equations in One Variable",items:[
        {code:"2.2",ws:"g9-algebra-2-2",title:"Solve Multi-step Linear Equations",sub:"Eid Al Etihad edition · 15 questions with hints and worked steps",file:"worksheets/g9-algebra-2-2-multi-step-equations.html"}]},
      {name:"Module 3",topic:"Linear Equations",items:[
        {code:"3.1",ws:"g9-algebra-3-1",title:"Linear Equations in Standard Form",sub:"Quiz · Eid Al Etihad edition · 14 questions with hints and worked steps",file:"worksheets/g9-algebra-3-1-linear-equations-standard-form.html"},
        {code:"3.2",ws:"g9-algebra-3-2",title:"Slopes of Lines and Rates of Change",sub:"Eid Al Etihad edition · 15 questions with hints and worked steps",file:"worksheets/g9-algebra-3-2-slopes-rates-of-change.html"}]},
      {name:"Module 4",topic:"Linear Functions and Models",items:[
        {code:"4.1",ws:"g9-algebra-4-1",title:"Relations and Functions",sub:"Eid Al Etihad edition · 15 questions with hints and worked steps",file:"worksheets/g9-algebra-4-1-relations-functions.html"}]}]}]},
  {id:"10",name:"Grade 10",course:"Geometry",terms:[
    {name:"Term 1",modules:[
      {name:"Module 13",topic:"Trigonometry with Right Triangles",items:[
        {code:"13.1",ws:"g10-geometry-13-1",title:"Tangent Ratio",sub:"Eid Al Etihad edition · 14 interactive questions with hints and worked steps",file:"worksheets/g10-geometry-13-1-tangent-ratio.html"}]}]}]},
  {id:"11",name:"Grade 11",course:"Mathematics",terms:[]},
  {id:"12",name:"Grade 12",course:"Calculus",terms:[
    {name:"Flipped Math Calculus · Version 1",modules:[
      {name:"Unit 1",topic:"Limits and Continuity",items:[
        {code:"1.1",ws:"g12-calc-1-1",title:"Can Change Occur at an Instant?",sub:"5 questions \u00b7 hints and worked steps",file:"worksheets/g12-calculus-1-1.html"},
        {code:"1.2",ws:"g12-calc-1-2",title:"Defining Limits and Using Limit Notation",sub:"5 questions \u00b7 hints and worked steps",file:"worksheets/g12-calculus-1-2.html"},
        {code:"1.3",ws:"g12-calc-1-3",title:"Limit Values from Graphs",sub:"5 questions \u00b7 hints and worked steps",file:"worksheets/g12-calculus-1-3.html"},
        {code:"1.4",ws:"g12-calc-1-4",title:"Limit Values from Tables",sub:"5 questions \u00b7 hints and worked steps",file:"worksheets/g12-calculus-1-4.html"},
        {code:"1.5",ws:"g12-calc-1-5",title:"Determining Limits Using Algebraic Properties",sub:"5 questions \u00b7 hints and worked steps",file:"worksheets/g12-calculus-1-5.html"},
        {code:"1.6",ws:"g12-calc-1-6",title:"Determining Limits Using Algebraic Manipulation",sub:"5 questions \u00b7 hints and worked steps",file:"worksheets/g12-calculus-1-6.html"},
        {code:"1.7",ws:"g12-calc-1-7",title:"Selecting Procedures for Determining Limits",sub:"5 questions \u00b7 hints and worked steps",file:"worksheets/g12-calculus-1-7.html"},
        {code:"1.8",ws:"g12-calc-1-8",title:"Determining Limits Using the Squeeze Theorem",sub:"5 questions \u00b7 hints and worked steps",file:"worksheets/g12-calculus-1-8.html"},
        {code:"1.9",ws:"g12-calc-1-9",title:"Connecting Multiple Representations of Limits",sub:"5 questions \u00b7 hints and worked steps",file:"worksheets/g12-calculus-1-9.html"},
        {code:"1.10",ws:"g12-calc-1-10",title:"Exploring Types of Discontinuities",sub:"5 questions \u00b7 hints and worked steps",file:"worksheets/g12-calculus-1-10.html"},
        {code:"1.11",ws:"g12-calc-1-11",title:"Defining Continuity at a Point",sub:"5 questions \u00b7 hints and worked steps",file:"worksheets/g12-calculus-1-11.html"},
        {code:"1.12",ws:"g12-calc-1-12",title:"Confirming Continuity over an Interval",sub:"5 questions \u00b7 hints and worked steps",file:"worksheets/g12-calculus-1-12.html"},
        {code:"1.13",ws:"g12-calc-1-13",title:"Removing Discontinuities",sub:"5 questions \u00b7 hints and worked steps",file:"worksheets/g12-calculus-1-13.html"},
        {code:"1.14",ws:"g12-calc-1-14",title:"Infinite Limits and Vertical Asymptotes",sub:"5 questions \u00b7 hints and worked steps",file:"worksheets/g12-calculus-1-14.html"},
        {code:"1.15",ws:"g12-calc-1-15",title:"Limits at Infinity and Horizontal Asymptotes",sub:"5 questions \u00b7 hints and worked steps",file:"worksheets/g12-calculus-1-15.html"},
        {code:"1.16",ws:"g12-calc-1-16",title:"Intermediate Value Theorem",sub:"5 questions \u00b7 hints and worked steps",file:"worksheets/g12-calculus-1-16.html"}]},
      {name:"Unit 2",topic:"Differentiation: Definition and Fundamental Properties",items:[
        {code:"2.1",ws:"g12-calc-2-1",title:"Defining Average and Instantaneous Rate of Change at a Point",sub:"5 questions \u00b7 hints and worked steps",file:"worksheets/g12-calculus-2-1.html"},
        {code:"2.2",ws:"g12-calc-2-2",title:"Defining the Derivative of a Function and Using Derivative Notation",sub:"5 questions \u00b7 hints and worked steps",file:"worksheets/g12-calculus-2-2.html"},
        {code:"2.3",ws:"g12-calc-2-3",title:"Estimating Derivatives of a Function at a Point",sub:"5 questions \u00b7 hints and worked steps",file:"worksheets/g12-calculus-2-3.html"},
        {code:"2.4",ws:"g12-calc-2-4",title:"Connecting Differentiability and Continuity",sub:"5 questions \u00b7 hints and worked steps",file:"worksheets/g12-calculus-2-4.html"},
        {code:"2.5",ws:"g12-calc-2-5",title:"Applying the Power Rule",sub:"5 questions \u00b7 hints and worked steps",file:"worksheets/g12-calculus-2-5.html"},
        {code:"2.6",ws:"g12-calc-2-6",title:"Derivative Rules: Constant, Sum, Difference, and Constant Multiple",sub:"5 questions \u00b7 hints and worked steps",file:"worksheets/g12-calculus-2-6.html"},
        {code:"2.7",ws:"g12-calc-2-7",title:"Derivatives of cos x, sin x, eˣ, and ln x",sub:"5 questions \u00b7 hints and worked steps",file:"worksheets/g12-calculus-2-7.html"},
        {code:"2.8",ws:"g12-calc-2-8",title:"The Product Rule",sub:"5 questions \u00b7 hints and worked steps",file:"worksheets/g12-calculus-2-8.html"},
        {code:"2.9",ws:"g12-calc-2-9",title:"The Quotient Rule",sub:"5 questions \u00b7 hints and worked steps",file:"worksheets/g12-calculus-2-9.html"},
        {code:"2.10",ws:"g12-calc-2-10",title:"Derivatives of tan x, cot x, sec x, csc x",sub:"5 questions \u00b7 hints and worked steps",file:"worksheets/g12-calculus-2-10.html"}]},
      {name:"Unit 3",topic:"Differentiation: Composite, Implicit, and Inverse Functions",items:[
        {code:"3.1",ws:"g12-calc-3-1",title:"The Chain Rule",sub:"5 questions \u00b7 hints and worked steps",file:"worksheets/g12-calculus-3-1.html"},
        {code:"3.2",ws:"g12-calc-3-2",title:"Implicit Differentiation",sub:"5 questions \u00b7 hints and worked steps",file:"worksheets/g12-calculus-3-2.html"},
        {code:"3.3",ws:"g12-calc-3-3",title:"Differentiating Inverse Functions",sub:"5 questions \u00b7 hints and worked steps",file:"worksheets/g12-calculus-3-3.html"},
        {code:"3.4",ws:"g12-calc-3-4",title:"Differentiating Inverse Trigonometric Functions",sub:"5 questions \u00b7 hints and worked steps",file:"worksheets/g12-calculus-3-4.html"},
        {code:"3.5",ws:"g12-calc-3-5",title:"Selecting Procedures for Calculating Derivatives",sub:"5 questions \u00b7 hints and worked steps",file:"worksheets/g12-calculus-3-5.html"},
        {code:"3.6",ws:"g12-calc-3-6",title:"Calculating Higher-Order Derivatives",sub:"5 questions \u00b7 hints and worked steps",file:"worksheets/g12-calculus-3-6.html"}]},
      {name:"Unit 4",topic:"Contextual Applications of Differentiation",items:[
        {code:"4.1",ws:"g12-calc-4-1",title:"Interpreting the Meaning of the Derivative in Context",sub:"5 questions \u00b7 hints and worked steps",file:"worksheets/g12-calculus-4-1.html"},
        {code:"4.2",ws:"g12-calc-4-2",title:"Straight-Line Motion: Connecting Position, Velocity, and Acceleration",sub:"5 questions \u00b7 hints and worked steps",file:"worksheets/g12-calculus-4-2.html"},
        {code:"4.3",ws:"g12-calc-4-3",title:"Rates of Change in Applied Contexts Other Than Motion",sub:"5 questions \u00b7 hints and worked steps",file:"worksheets/g12-calculus-4-3.html"},
        {code:"4.4",ws:"g12-calc-4-4",title:"Introduction to Related Rates",sub:"5 questions \u00b7 hints and worked steps",file:"worksheets/g12-calculus-4-4.html"},
        {code:"4.5",ws:"g12-calc-4-5",title:"Solving Related Rates Problems",sub:"5 questions \u00b7 hints and worked steps",file:"worksheets/g12-calculus-4-5.html"},
        {code:"4.6",ws:"g12-calc-4-6",title:"Approximating Values of a Function Using Local Linearity and Linearization",sub:"5 questions \u00b7 hints and worked steps",file:"worksheets/g12-calculus-4-6.html"},
        {code:"4.7",ws:"g12-calc-4-7",title:"Using L'Hôpital's Rule for Determining Limits of Indeterminate Forms",sub:"5 questions \u00b7 hints and worked steps",file:"worksheets/g12-calculus-4-7.html"}]},
      {name:"Unit 5",topic:"Analytical Applications of Differentiation",items:[
        {code:"5.1",ws:"g12-calc-5-1",title:"Using the Mean Value Theorem",sub:"5 questions \u00b7 hints and worked steps",file:"worksheets/g12-calculus-5-1.html"},
        {code:"5.2",ws:"g12-calc-5-2",title:"Extreme Value Theorem, Global Versus Local Extrema, and Critical Points",sub:"5 questions \u00b7 hints and worked steps",file:"worksheets/g12-calculus-5-2.html"},
        {code:"5.3",ws:"g12-calc-5-3",title:"Determining Intervals on Which a Function Is Increasing or Decreasing",sub:"5 questions \u00b7 hints and worked steps",file:"worksheets/g12-calculus-5-3.html"},
        {code:"5.4",ws:"g12-calc-5-4",title:"Using the First Derivative Test to Determine Relative (Local) Extrema",sub:"5 questions \u00b7 hints and worked steps",file:"worksheets/g12-calculus-5-4.html"},
        {code:"5.5",ws:"g12-calc-5-5",title:"Using the Candidates Test to Determine Absolute (Global) Extrema",sub:"5 questions \u00b7 hints and worked steps",file:"worksheets/g12-calculus-5-5.html"},
        {code:"5.6",ws:"g12-calc-5-6",title:"Determining Concavity of Functions over Their Domains",sub:"5 questions \u00b7 hints and worked steps",file:"worksheets/g12-calculus-5-6.html"},
        {code:"5.7",ws:"g12-calc-5-7",title:"Using the Second Derivative Test to Determine Extrema",sub:"5 questions \u00b7 hints and worked steps",file:"worksheets/g12-calculus-5-7.html"},
        {code:"5.8",ws:"g12-calc-5-8",title:"Sketching Graphs of Functions and Their Derivatives",sub:"5 questions \u00b7 hints and worked steps",file:"worksheets/g12-calculus-5-8.html"},
        {code:"5.9",ws:"g12-calc-5-9",title:"Connecting a Function, Its First Derivative, and Its Second Derivative",sub:"5 questions \u00b7 hints and worked steps",file:"worksheets/g12-calculus-5-9.html"},
        {code:"5.10",ws:"g12-calc-5-10",title:"Introduction to Optimization Problems",sub:"5 questions \u00b7 hints and worked steps",file:"worksheets/g12-calculus-5-10.html"},
        {code:"5.11",ws:"g12-calc-5-11",title:"Solving Optimization Problems",sub:"5 questions \u00b7 hints and worked steps",file:"worksheets/g12-calculus-5-11.html"},
        {code:"5.12",ws:"g12-calc-5-12",title:"Exploring Behaviors of Implicit Relations",sub:"5 questions \u00b7 hints and worked steps",file:"worksheets/g12-calculus-5-12.html"}]},
      {name:"Unit 6",topic:"Integration and Accumulation of Change",items:[
        {code:"6.1",ws:"g12-calc-6-1",title:"Exploring Accumulation of Change",sub:"5 questions \u00b7 hints and worked steps",file:"worksheets/g12-calculus-6-1.html"},
        {code:"6.2",ws:"g12-calc-6-2",title:"Approximating Areas with Riemann Sums",sub:"5 questions \u00b7 hints and worked steps",file:"worksheets/g12-calculus-6-2.html"},
        {code:"6.3",ws:"g12-calc-6-3",title:"Riemann Sums, Summation Notation, and Definite Integral Notation",sub:"5 questions \u00b7 hints and worked steps",file:"worksheets/g12-calculus-6-3.html"},
        {code:"6.4",ws:"g12-calc-6-4",title:"The Fundamental Theorem of Calculus and Accumulation Functions",sub:"5 questions \u00b7 hints and worked steps",file:"worksheets/g12-calculus-6-4.html"},
        {code:"6.5",ws:"g12-calc-6-5",title:"Interpreting the Behavior of Accumulation Functions Involving Area",sub:"5 questions \u00b7 hints and worked steps",file:"worksheets/g12-calculus-6-5.html"},
        {code:"6.6",ws:"g12-calc-6-6",title:"Applying Properties of Definite Integrals",sub:"5 questions \u00b7 hints and worked steps",file:"worksheets/g12-calculus-6-6.html"},
        {code:"6.7",ws:"g12-calc-6-7",title:"The Fundamental Theorem of Calculus and Definite Integrals",sub:"5 questions \u00b7 hints and worked steps",file:"worksheets/g12-calculus-6-7.html"},
        {code:"6.8",ws:"g12-calc-6-8",title:"Finding Antiderivatives and Indefinite Integrals: Basic Rules and Notation",sub:"5 questions \u00b7 hints and worked steps",file:"worksheets/g12-calculus-6-8.html"},
        {code:"6.9",ws:"g12-calc-6-9",title:"Integrating Using Substitution",sub:"5 questions \u00b7 hints and worked steps",file:"worksheets/g12-calculus-6-9.html"},
        {code:"6.10",ws:"g12-calc-6-10",title:"Integrating Functions Using Long Division and Completing the Square",sub:"5 questions \u00b7 hints and worked steps",file:"worksheets/g12-calculus-6-10.html"},
        {code:"6.11",ws:"g12-calc-6-11",title:"Integration by Parts",sub:"5 questions \u00b7 hints and worked steps",file:"worksheets/g12-calculus-6-11.html"},
        {code:"6.12",ws:"g12-calc-6-12",title:"Integrating Using Linear Partial Fractions",sub:"5 questions \u00b7 hints and worked steps",file:"worksheets/g12-calculus-6-12.html"},
        {code:"6.13",ws:"g12-calc-6-13",title:"Evaluating Improper Integrals",sub:"5 questions \u00b7 hints and worked steps",file:"worksheets/g12-calculus-6-13.html"},
        {code:"6.14",ws:"g12-calc-6-14",title:"Selecting Techniques for Antidifferentiation",sub:"5 questions \u00b7 hints and worked steps",file:"worksheets/g12-calculus-6-14.html"}]},
      {name:"Unit 7",topic:"Differential Equations",items:[
        {code:"7.1",ws:"g12-calc-7-1",title:"Modeling Situations with Differential Equations",sub:"5 questions \u00b7 hints and worked steps",file:"worksheets/g12-calculus-7-1.html"},
        {code:"7.2",ws:"g12-calc-7-2",title:"Verifying Solutions for Differential Equations",sub:"5 questions \u00b7 hints and worked steps",file:"worksheets/g12-calculus-7-2.html"},
        {code:"7.3",ws:"g12-calc-7-3",title:"Sketching Slope Fields",sub:"5 questions \u00b7 hints and worked steps",file:"worksheets/g12-calculus-7-3.html"},
        {code:"7.4",ws:"g12-calc-7-4",title:"Reasoning Using Slope Fields",sub:"5 questions \u00b7 hints and worked steps",file:"worksheets/g12-calculus-7-4.html"},
        {code:"7.5",ws:"g12-calc-7-5",title:"Approximating Solutions Using Euler's Method",sub:"5 questions \u00b7 hints and worked steps",file:"worksheets/g12-calculus-7-5.html"},
        {code:"7.6",ws:"g12-calc-7-6",title:"Finding General Solutions Using Separation of Variables",sub:"5 questions \u00b7 hints and worked steps",file:"worksheets/g12-calculus-7-6.html"},
        {code:"7.7",ws:"g12-calc-7-7",title:"Finding Particular Solutions Using Initial Conditions and Separation of Variables",sub:"5 questions \u00b7 hints and worked steps",file:"worksheets/g12-calculus-7-7.html"},
        {code:"7.8",ws:"g12-calc-7-8",title:"Exponential Models with Differential Equations",sub:"5 questions \u00b7 hints and worked steps",file:"worksheets/g12-calculus-7-8.html"},
        {code:"7.9",ws:"g12-calc-7-9",title:"Logistic Models with Differential Equations",sub:"5 questions \u00b7 hints and worked steps",file:"worksheets/g12-calculus-7-9.html"}]},
      {name:"Unit 8",topic:"Applications of Integration",items:[
        {code:"8.1",ws:"g12-calc-8-1",title:"Finding the Average Value of a Function on an Interval",sub:"5 questions \u00b7 hints and worked steps",file:"worksheets/g12-calculus-8-1.html"},
        {code:"8.2",ws:"g12-calc-8-2",title:"Connecting Position, Velocity, and Acceleration of Functions Using Integrals",sub:"5 questions \u00b7 hints and worked steps",file:"worksheets/g12-calculus-8-2.html"},
        {code:"8.3",ws:"g12-calc-8-3",title:"Using Accumulation Functions and Definite Integrals in Applied Contexts",sub:"5 questions \u00b7 hints and worked steps",file:"worksheets/g12-calculus-8-3.html"},
        {code:"8.4",ws:"g12-calc-8-4",title:"Finding the Area Between Curves Expressed as Functions of x",sub:"5 questions \u00b7 hints and worked steps",file:"worksheets/g12-calculus-8-4.html"},
        {code:"8.5",ws:"g12-calc-8-5",title:"Finding the Area Between Curves Expressed as Functions of y",sub:"5 questions \u00b7 hints and worked steps",file:"worksheets/g12-calculus-8-5.html"},
        {code:"8.6",ws:"g12-calc-8-6",title:"Finding the Area Between Curves That Intersect at More Than Two Points",sub:"5 questions \u00b7 hints and worked steps",file:"worksheets/g12-calculus-8-6.html"},
        {code:"8.7",ws:"g12-calc-8-7",title:"Volumes with Cross Sections: Squares and Rectangles",sub:"5 questions \u00b7 hints and worked steps",file:"worksheets/g12-calculus-8-7.html"},
        {code:"8.8",ws:"g12-calc-8-8",title:"Volumes with Cross Sections: Triangles and Semicircles",sub:"5 questions \u00b7 hints and worked steps",file:"worksheets/g12-calculus-8-8.html"},
        {code:"8.9",ws:"g12-calc-8-9",title:"Volume with Disc Method: Revolving Around the x- or y-Axis",sub:"5 questions \u00b7 hints and worked steps",file:"worksheets/g12-calculus-8-9.html"},
        {code:"8.10",ws:"g12-calc-8-10",title:"Volume with Disc Method: Revolving Around Other Axes",sub:"5 questions \u00b7 hints and worked steps",file:"worksheets/g12-calculus-8-10.html"},
        {code:"8.11",ws:"g12-calc-8-11",title:"Volume with Washer Method: Revolving Around the x- or y-Axis",sub:"5 questions \u00b7 hints and worked steps",file:"worksheets/g12-calculus-8-11.html"},
        {code:"8.12",ws:"g12-calc-8-12",title:"Volume with Washer Method: Revolving Around Other Axes",sub:"5 questions \u00b7 hints and worked steps",file:"worksheets/g12-calculus-8-12.html"},
        {code:"8.13",ws:"g12-calc-8-13",title:"The Arc Length of a Smooth, Planar Curve and Distance Traveled",sub:"5 questions \u00b7 hints and worked steps",file:"worksheets/g12-calculus-8-13.html"}]},
      {name:"Unit 9",topic:"Parametric Equations, Polar Coordinates, and Vector-Valued Functions (BC)",items:[
        {code:"9.1",ws:"g12-calc-9-1",title:"Defining and Differentiating Parametric Equations",sub:"5 questions \u00b7 hints and worked steps",file:"worksheets/g12-calculus-9-1.html"},
        {code:"9.2",ws:"g12-calc-9-2",title:"Second Derivatives of Parametric Equations",sub:"5 questions \u00b7 hints and worked steps",file:"worksheets/g12-calculus-9-2.html"},
        {code:"9.3",ws:"g12-calc-9-3",title:"Finding Arc Lengths of Curves Given by Parametric Equations",sub:"5 questions \u00b7 hints and worked steps",file:"worksheets/g12-calculus-9-3.html"},
        {code:"9.4",ws:"g12-calc-9-4",title:"Defining and Differentiating Vector-Valued Functions",sub:"5 questions \u00b7 hints and worked steps",file:"worksheets/g12-calculus-9-4.html"},
        {code:"9.5",ws:"g12-calc-9-5",title:"Integrating Vector-Valued Functions",sub:"5 questions \u00b7 hints and worked steps",file:"worksheets/g12-calculus-9-5.html"},
        {code:"9.6",ws:"g12-calc-9-6",title:"Solving Motion Problems Using Parametric and Vector-Valued Functions",sub:"5 questions \u00b7 hints and worked steps",file:"worksheets/g12-calculus-9-6.html"},
        {code:"9.7",ws:"g12-calc-9-7",title:"Defining Polar Coordinates and Differentiating in Polar Form",sub:"5 questions \u00b7 hints and worked steps",file:"worksheets/g12-calculus-9-7.html"},
        {code:"9.8",ws:"g12-calc-9-8",title:"Finding the Area of a Polar Region or the Area Bounded by a Single Polar Curve",sub:"5 questions \u00b7 hints and worked steps",file:"worksheets/g12-calculus-9-8.html"},
        {code:"9.9",ws:"g12-calc-9-9",title:"Finding the Area of the Region Bounded by Two Polar Curves",sub:"5 questions \u00b7 hints and worked steps",file:"worksheets/g12-calculus-9-9.html"}]},
      {name:"Unit 10",topic:"Infinite Sequences and Series (BC)",items:[
        {code:"10.1",ws:"g12-calc-10-1",title:"Defining Convergent and Divergent Infinite Series",sub:"5 questions \u00b7 hints and worked steps",file:"worksheets/g12-calculus-10-1.html"},
        {code:"10.2",ws:"g12-calc-10-2",title:"Working with Geometric Series",sub:"5 questions \u00b7 hints and worked steps",file:"worksheets/g12-calculus-10-2.html"},
        {code:"10.3",ws:"g12-calc-10-3",title:"The nth Term Test for Divergence",sub:"5 questions \u00b7 hints and worked steps",file:"worksheets/g12-calculus-10-3.html"},
        {code:"10.4",ws:"g12-calc-10-4",title:"Integral Test for Convergence",sub:"5 questions \u00b7 hints and worked steps",file:"worksheets/g12-calculus-10-4.html"},
        {code:"10.5",ws:"g12-calc-10-5",title:"Harmonic Series and p-Series",sub:"5 questions \u00b7 hints and worked steps",file:"worksheets/g12-calculus-10-5.html"},
        {code:"10.6",ws:"g12-calc-10-6",title:"Comparison Tests for Convergence",sub:"5 questions \u00b7 hints and worked steps",file:"worksheets/g12-calculus-10-6.html"},
        {code:"10.7",ws:"g12-calc-10-7",title:"Alternating Series Test for Convergence",sub:"5 questions \u00b7 hints and worked steps",file:"worksheets/g12-calculus-10-7.html"},
        {code:"10.8",ws:"g12-calc-10-8",title:"Ratio Test for Convergence",sub:"5 questions \u00b7 hints and worked steps",file:"worksheets/g12-calculus-10-8.html"},
        {code:"10.9",ws:"g12-calc-10-9",title:"Determining Absolute or Conditional Convergence",sub:"5 questions \u00b7 hints and worked steps",file:"worksheets/g12-calculus-10-9.html"},
        {code:"10.10",ws:"g12-calc-10-10",title:"Alternating Series Error Bound",sub:"5 questions \u00b7 hints and worked steps",file:"worksheets/g12-calculus-10-10.html"},
        {code:"10.11",ws:"g12-calc-10-11",title:"Finding Taylor Polynomial Approximations of Functions",sub:"5 questions \u00b7 hints and worked steps",file:"worksheets/g12-calculus-10-11.html"},
        {code:"10.12",ws:"g12-calc-10-12",title:"Lagrange Error Bound",sub:"5 questions \u00b7 hints and worked steps",file:"worksheets/g12-calculus-10-12.html"},
        {code:"10.13",ws:"g12-calc-10-13",title:"Radius and Interval of Convergence of Power Series",sub:"5 questions \u00b7 hints and worked steps",file:"worksheets/g12-calculus-10-13.html"},
        {code:"10.14",ws:"g12-calc-10-14",title:"Finding Taylor or Maclaurin Series for a Function",sub:"5 questions \u00b7 hints and worked steps",file:"worksheets/g12-calculus-10-14.html"},
        {code:"10.15",ws:"g12-calc-10-15",title:"Representing Functions as a Power Series",sub:"5 questions \u00b7 hints and worked steps",file:"worksheets/g12-calculus-10-15.html"}]}]}]}
];
/* Worksheets made with the Worksheet builder (approved on admin.html) are added at run time from the school's
   Apps Script (?a=wslist). They all open on worksheets/w.html?id=…  */
function mergeLive(list){
  const num=c=>String(c).split(".").map(Number);
  (list||[]).forEach(w=>{
    const g=GRADES.find(x=>x.id===String(w.grade));if(!g)return;
    const tn=w.term||"Term 1",mn=w.module||"Worksheets";
    let t=g.terms.find(x=>x.name===tn);if(!t){t={name:tn,modules:[]};g.terms.push(t);g.terms.sort((a,b)=>a.name.localeCompare(b.name,undefined,{numeric:true}));}
    let m=t.modules.find(x=>x.name===mn);if(!m){m={name:mn,topic:w.topic||"",items:[]};t.modules.push(m);t.modules.sort((a,b)=>a.name.localeCompare(b.name,undefined,{numeric:true}));}
    const file="worksheets/w.html?id="+w.id;if(m.items.some(i=>i.file===file))return;
    m.items.push({code:String(w.code),ws:"w-"+w.id,title:String(w.title),sub:(w.n?w.n+" questions":"Questions")+" with hints and worked steps",file,dyn:true});
    m.items.sort((a,b)=>{const x=num(a.code),y=num(b.code);return (x[0]-y[0])||((x[1]||0)-(y[1]||0));});
  });
}
