FROM contribsys/faktory:latest
ENV FAKTORY_PASSWORD=aErlnoRkA3r5v0D
EXPOSE 7419
EXPOSE 7420
CMD ["/faktory", "-b", ":7419", "-w", ":7420", "-e", "production"]
