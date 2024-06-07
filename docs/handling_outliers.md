# Handling Wild and Outlier Rates

In the project, maintaining the integrity of user-generated ratings is crucial. To ensure that ratings are genuine and fair, we have a Rate Weighting System(instead of calculating average rate in realtime and based on exact rates' scores) which is implemented with several methods to recognize and handle wild and outlier rates. Below are the detailed methods and optimizations:

## Methods for Recognizing Outlier and Wild Rates

### 1. Asynchronous Periodic Task

**Description**:
Calculating rate weight and post average rate as an asynchronous periodic task allows us to observe rates over a larger time period (approximately 5 hours) and ensure fair weighting and average rate calculation.

**Implementation**:

- Set up an asynchronous periodic task to calculate rate weight and post average rate.
- Gather rates submitted within the last 5 hours and calculate their weights.
- Update the average rate of each post based on the calculated weights.

### 2. User Authentication

**Description**:
Requiring users to authenticate before they can rate a post ensures that we can track individual user behavior. This allows us to identify and restrict any suspicious or abnormal rating activities on a per-user basis.

**Implementation**:

- Users must log in before they can submit a rating.
- Use secure authentication protocols (JWT) to verify user identities.
- Track user ratings (number of rates and total rates' weights) to monitor patterns over time.

### 3. User Account Age

**Description**:
Evaluating the age of a user’s account helps to detect ratings from newly created accounts that might be used for manipulative purposes.

**Implementation**:

- Record the account creation date for each user.
- Assign lower credibility to ratings from accounts that are very new (less than 30 days).

**Weight Adjustment**:

- New accounts (less than 30 days old) receive lower weight on their ratings.
- Established accounts receive higher weight, reflecting their credibility.

### 4. User Activity and Rate Quality

**Description**:
Tracking user activity and rate quality involves monitoring the number of ratings a user has submitted and calculating the average weight of those ratings. This helps in assessing the overall quality of the user's contributions and their engagement with the site.

**Implementation**:

- Track the count of ratings submitted by each user.
- Calculate the average weight of the user’s ratings using the `rate_quality` property.

**Weight Adjustment**:

- Accounts with higher `rate_quality` receive higher weight on their ratings.
- Accounts with a larger number of ratings receive higher weight.

### 5. Rate Limiting

**Description**:
Implementing rate limiting ensures that users can only submit a specific number of ratings within a given time frame. This prevents rapid-fire rating, which is often a sign of manipulation.

**Implementation**:

- Set a limit on the number of ratings a user can submit in an hour, day, or week.
- Temporarily block users from rating if they exceed the limit.

### 6. Outlier Rates (Using Standard Deviation)

**Description**:
To identify and potentially down-weight anomalous voting patterns, such as large clusters of very high or very low ratings, we use the empirical rule (68-95-99.7 rule). This method requires at least 1000 ratings for a post to recognize outlier rates.

**Implementation**:

- Calculate the average and standard deviation of ratings for each post.
- Identify ratings that fall outside of one standard deviation from the average.
- Outlier ratings are given zero weight and do not affect the average post rating.

**Weight Adjustment**:

- Outlier ratings (outside one standard deviation) receive zero weight.

### 7. Post Average Rating Speed

**Description**:
Monitoring the average rating speed at which users submit ratings can reveal unusual patterns.

**Implementation**:

- Calculate the average rating speed per 5-hour interval for each post.
- Compare the number of ratings received in the last 5 hours to the average speed.

**Weight Adjustment**:

- If the number of ratings received in the last 5 hours is significantly higher than the average speed, the weight of these ratings is reduced to account for potential bias.
- Ratings submitted within the normal average speed are given higher weight.
