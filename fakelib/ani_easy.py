import matplotlib.pyplot as plt
import matplotlib.animation as animation
def ani_easy(tas, cmap='BrBG'):
	# Get a handle on the figure and the axes
	fig, ax = plt.subplots(figsize=(12,6))

	# Plot the initial frame. 
	cax = tas[0,:,:].plot(
	    add_colorbar=True,
            cmap=cmap,
	    #cmap='BrBG',
	    #cmap='magma',
	#     vmin=-40, vmax=40,
	    cbar_kwargs={
		'extend':'neither'
	    }
	)

	num_frames = tas.shape[0]
	# Next we need to create a function that updates the values for the colormesh, as well as the title.
	def animate(frame):
	    cax.set_array(tas[frame,:,:].values.flatten())
	    ax.set_title("Time = " + str(tas.coords['time'].values[frame])[:13])

	# Finally, we use the animation module to create the animation.
	ani = animation.FuncAnimation(
	    fig,             # figure
	    animate,         # name of the function above
	    frames=num_frames,       # Could also be iterable or list
	    interval=200     # ms between frames
	)

	return ani
