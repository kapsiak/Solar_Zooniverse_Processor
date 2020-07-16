# Todo

## Questions

1. Which tools will we be using.
2. Data aggregation methods. How do we take start points and rectangle spread over several frames and produce actual results. Size varies a lot (7Mb-100Mb)
3. Size limits in zooniverse? 6 Events produced over 2 thousand fits files
4. Including a movie? How to do it? Size limit? 
5. Write up? Display/help needed?
6. Better rectangle tool? A little cumbersome now/don't want people getting bored/frustrated.




## Aggregation

We must begin the process of writing the data importers and aggregators

### General Workflow

Below the general idea for the workflow. It is complicated by the fact that event sets may be divided between multiple subjects.
It is double complicated since there may be multiple jets in a single subject. 

1. Download data from zooniverse
2. Each subject will have attached the following data: 
    - The frame in which the jet(s) begins, and location on that frame
    - The frame in which the jet(s) end, and location on that frame
    - Zero or more rectangular boxes on some of the frames indicating the extent of the jet 
3. We want to convert this data to a dict?
4. This data must be aggregated

There are a couple of ways we could think about aggregation.

In terms of the chronological questions, it seems that the most efficient way might be to simply average over all responses, and take the closest frame.
Uncertainties could then be extracted in the normal way, as for any one dimensional dataset. 

For point based spatial questions, we could first "collapse" along the time axis, then use some sort of least distance algorithm.

In the end we want a "categorized jet" table with the following columns:
    - Event Start Time
    - Base Point (Likely in HPC coords)
    - Event End Time
    - Event Extent (possibly as a function of time) ( Visual Area, Rectangle in HPC)
    - Uncertainties in the above
    - Foreign Key -> Fits File   ( Fits file with the necessary header information)
    - Foreign Key -> Visual File (Actualy image that was used in zooniverse)
    - Foreign Key -> Solar Event (Hek event this came from)

We can also perhaps ask users to point out locations where they see something interesting.

Will probably pick just 2 or so, since many are actually related already
    

Allow for export as csv with the following columns:
    - Event Start Time
    - Base Point
    - Event End Time
    - Event Extent (possibly as a function of time)
    - Uncertainties in the above
    - Sol Standard
    - Interest Level

This would allow for a high level of portability.
Could probably also find a way to convert it to IDL data structure sophie was talking about



Generate Images showing this extend (additional Visual Files)


## Stability and Maintainability

### Tests

Need more tests, large swaths of the program are uncovered. 

### Documentation

Need more documentation. 


