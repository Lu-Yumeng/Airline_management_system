# default draw an image
		query = """SELECT price, purchase_date FROM ticket NATURAL JOIN purchases NATURAL JOIN flight WHERE customer_email = '%s'"""
		cursor = conn.cursor()
		cursor.execute(query % session['username'])
		info = cursor.fetchall()
		cursor.close()
		half_ago = cur - datetime.timedelta(days=183)
		last_month = cur.month
		begin_month = last_month-6
		spent = [0 for i in range(6)]
		for record in info:
			if cur > record['purchase_date'] >= half_ago:
				mon = record['purchase_date'].month
				if last_month >= mon:
					spent[(5-last_month+mon)%6] += record['price']
				else:
					spent[(-12-last_month+mon)%6] += record['price']
		x_axis = [month[i] for i in range(begin_month,begin_month+6)]
		plt.bar(x_axis,spent)
		plt.title('Monthly spent')
		plt.xlabel('Month')
		plt.ylabel('Spent')
		for a,b in zip(x_axis,spent):
			plt.text(a,b, b, ha='center', va= 'bottom',fontsize=7)
		# save as binary file
		buffer = BytesIO()
		plt.savefig(buffer)
		plot_data = buffer.getvalue()
		# 将matplotlib图片转换为HTML
		imb = base64.b64encode(plot_data)  # 对plot_data进行编码
		ims = imb.decode()
		image = "data:image/png;base64," + ims

		# return the form of view commission
		try:
			if request.form["begin_date"]:
				begin = request.form['begin_date']
				begin = datetime.datetime.strptime(begin,'%Y-%m-%d')
				year2 = begin.year
				month2 = begin.month
			if request.form['end_date']:
				end = request.form['end_date']
				year1 = end.year
				month1 = end.month
			else:
				year1 = cur.year
				month1 = cur.month
			delta_month = (year1-year2)*12+(month1-month2)+1
			ago = cur - datetime.timedelta(days=delta_month*30)
			last_month = cur.month
			begin_month = last_month-delta_month
			spent = [0 for i in range(delta_month)]
			for record in info:
				if cur > record['purchase_date'] >= ago:
					mon = record['purchase_date'].month
					year = record['purchase_date'].year
					cur_delta_month = (year1-year)*12+(month1-mon)
					spent[(delta_month -1- cur_delta_month)%delta_month] += record['price']
			x_axis = [month[i] for i in range(begin_month,begin_month+delta_month)]
			print(spent,x_axis)
			plt.clf()
			plt.bar(x_axis,spent)
			plt.title('Monthly spent')
			plt.xlabel('Month')
			plt.ylabel('Spent')
			for a,b in zip(x_axis,spent):
				plt.text(a,b, b, ha='center', va= 'bottom',fontsize=7)
			# save as binary file
			buffer1 = BytesIO()
			plt.savefig(buffer1)
			plot_data = buffer1.getvalue()
			# 将matplotlib图片转换为HTML
			imb = base64.b64encode(plot_data)  # 对plot_data进行编码
			ims = imb.decode()
			image = "data:image/png;base64," + ims
			return render_template("agent_home.html", search_flight = data, bar_chart = image, month_money = month_money)
		except:
			print("Not form View Commission or no start date")
		# return the form of checking flights 








        <script>
        const yeard = JSON.parse(' {{yeardata | tojson| safe}} ')
        const halfd = JSON.parse(' {{halfdata | tojson| safe}} ')
        console.log(halfd)
        
        const SimpleBar = () => {
            const yeard = useData(yeard)
            const halfd = useData(halfd)
            return <svg className={'svg'} >
                <Draw yeard={yeard} halfd={halfd} />
                </svg>
        

        }
        
        function Draw(props){
            const {halfd, yeard} = props

            const height = 200
            const width = 300
            const margin = 40

            const xScaleLeft = d3.scaleBand()
                    .range([0, width])
                    .domain(halfd.map(d => {return d.customer_email}));

            const yScaleLeft = d3.scaleLinear()
                    .range([0, height])
                    .domain([0, d3.max(halfd, d => d.totnum)]).nice();

            return <g>
                {<line x1={0} y1={height} x2={width} y2={height} stroke='black'/>}
                {xScaleLeft.domain().map(tickValue =>
                    <g key={tickValue} transform={`translate(${xScaleLeft(tickValue)}, 0)`}>
                        <line y1={height} y2={height-5} stroke='black' />
                    </g>
                    )} 
        
                {<line y1={height} y2={0} stroke='black' />}
                {yScaleLeft.ticks(5).map(tickValue => 
                    <g key={tickValue} transform={`translate(-10, ${yScaleLeft(tickValue)})`}>
                    <line x2={10} stroke='black' />
                    <text style={{ textAnchor:'end', fontSize:'12px' }} >
                        {tickValue}
                    </text>
                    </g>
                )} 

                {halfd.map(d => {
                        return <rect key={d.customer_email} 
                        x={xScaleLeft(d.customer_email)} y={yScaleLeft(d.totnum)}
                        width={xScaleLeft.bandwidth()} height={height-yScaleLeft(d.totnum)} 
                        fill={'steelblue'} stroke={"black"}  />                            
                    })}
                </g>
        }

    ReactDOM.render( <SimpleBar />, document.getElementById('bar'));
    </script>   