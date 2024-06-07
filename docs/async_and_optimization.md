# Code Optimization and Asynchronous Tasks

To ensure efficient performance and accuracy in our rating calculations, we have implemented various asynchronous tasks and optimization techniques. This section outlines the key goals of these asynchronous tasks and the overall optimization strategy employed in our project.

## Code Optimization

### Efficient Database Queries

**Description**:
Optimizing database queries ensures our application performs well under load. We focus on using indexed fields, avoiding N+1 query problems, and selecting only necessary fields.

**Strategies**:

- Use indexed fields for faster query performance(Rate model).
- Avoid N+1 query problems by using `select_related` and `prefetch_related`.
- Select only necessary fields using `values`.
- Buck update to reduce database queries.
- ...

### Caching

**Description**:
Implementing caching mechanisms reduces the load on the database by storing frequently accessed data in memory.

**Strategies**:

- Cache results of expensive queries and computations(cache average rate and rate count in PostView).

### Asynchronous Processing

**Description**:
Offloading time-consuming tasks to asynchronous workers prevents blocking the main application thread and ensures smoother performance.

**Strategies**:

- Use Celery for background task processing.
- Schedule periodic tasks for regular maintenance and data updates.

For more details refer to [async tasks](#asynchronous-tasks)

### Real-time and Periodic Updates

**Description**:
Combining real-time updates for critical operations with periodic tasks for batch updates ensures efficiency and accuracy.

**Strategies**:

- Real-time updates: Immediate updates for total rates sum each time a new rate is added.
- Periodic updates: Background tasks (e.g., every 5 hours) to calculate and update total weighted rates sum and other metrics.

### Optimized Average Rate Calculation

**Description**:
Maintaining a running sum of rates and weighted metrics optimizes the calculation of average rates, avoiding the need to retrieve and process all rates for a post each time the average is calculated.

**Benefits**:

- Improves efficiency, especially as the number of rates increases.
- Ensures that the average rate calculation is quick and does not degrade with more data.

### Clustered Pagination

**Description**:
Using clustered pagination for large datasets, because it doesn't require the database to skip over records(in compare to off-set).

**Benefits**:

- Efficiency, especially for large datasets.
- Stable when dealing with data that is being inserted or deleted concurrently.


## Asynchronous Tasks

### Purpose

The primary purpose of our asynchronous tasks is to handle more complex calculations and updates in the background, ensuring that the main application remains responsive and efficient. Specifically, we use asynchronous tasks to calculate the weighted rates count and total weighted rates sum for posts. 

### Key Goals

1. **Efficient Calculation of Weighted Metrics**:

    - Asynchronous tasks are responsible for calculating weighted metrics such as the weighted rates count and total weighted rates sum. These calculations are more intensive and are handled in the background to prevent performance bottlenecks.

2. **Complex Calculation of Non-Realtime Metrics**:

    - Asynchronous tasks are responsible for calculating Non-Realtime Metrics such as users' rate weight and posts' average rate speed. Handling these complex calculations in background improves performance.

