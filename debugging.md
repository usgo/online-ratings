# Debugging

## Docker

For those unfamiliar with docker (and even for those that are) it's often nice
to have a recipe book af debugging techniques.

* Remove All containers
  * `docker rm $(docker ps --no-trunc -aq)`
* Remove/Clean up danglinge/unattached images
  * `docker images -q --filter "dangling=true" | xargs docker rmi`
* Stop all containers
  * `docker stop $(docker ps -a -q)`
* Enter a container for debugging
  * `docker exec -it [container-id] /bin/bash`
* Build and run image in current directory (e.g., for the loopback image)
  * `docker build -t loopback .`
  * `docker run --name run-loopback -d -rm loopback`
  * docker run --publish 3000:3000 --name run-loopback --rm loopback
* Build but not run:
  * `docker run --rm -v "$PWD":/usr/src/myapp -w /usr/src/myapp golang:1.7 go build -v`

### Debugging links

Docker links are stored in two places: environment variables and in the
`/etc/hosts` file. To print all the enivorment variables, you can run:

```
printenv
```
