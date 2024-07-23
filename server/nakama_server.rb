SensorValue = Struct.new(:value, :time)

class SensorValuesFetcher

   def self.getValue(value, id)
      case value
      when :water_ph
         return rand(4...15) + rand.round(2)
      when :water_ec
         return rand(1...11) + rand.round(2)
      when :water_temp
         return rand(11...35) + rand.round(2)
      when :test_call
         return number = case rand*100
            when 0...7.37 then false
            when 7.37...100 then true
            end
      end
   end

end

class NakamaServerStartup


   @instance_id
   @server_state

   @latest_values = {
      :water_temp => SensorValue.new(value: nil, time: nil),
      :water_ph => SensorValue.new(value: nil, time: nil),
      :water_ec => SensorValue.new(value: nil, time: nil),
   }

   def self.getId
      begin
         p "New server instance id: 1234"
         return 1234
      rescue => error
         p "failed to create server instance id, ask for help"
         return nil
      end
   end

   begin
      require 'sinatra'
      require 'sinatra/base'
      require 'arduino'

      p "require gems SUCCESS"
   rescue LoadError => error
      p error
      p "failed to require gems, installing gems"
      begin
         bundleInstall = system("bundle install")
         if !bundleInstall
            raise "bundle install FAILED"
         end
         require 'sinatra'
         require 'sinatra/base'
         require 'arduino'
      rescue => error
         p error
         p "failed to install gems, ask for help"
      rescue LoadError => error
         p error
         p "failed to require gems again, try restarting"
      end
   end

   @instance_id = NakamaServerStartup.getId()

   begin
      Sinatra::Base.get '/test_call' do
         '{
         "test_result":'+"#{SensorValuesFetcher.getValue(:test_call, @instance_id)}
      }"
      end
      p "created test_call endpoint"

      Sinatra::Base.get '/water_ph' do
         '{
         "value":'+"#{SensorValuesFetcher.getValue(:water_ph, @instance_id)}
      }"
      end
      p "created water_ph endpoint"

      Sinatra::Base.get '/water_temperature' do
         '{
         "value":'+"#{SensorValuesFetcher.getValue(:water_temp, @instance_id)}
      }"
      end
      p "created water_temperature endpoint"

      Sinatra::Base.get '/water_ec' do
         '{
         "value":'+"#{SensorValuesFetcher.getValue(:water_ec, @instance_id)}
      }"
      end
      p "created water_ec endpoint"

   rescue => error
      p error
      p "failed to create endpoints, ask for help"
   end

end


newStartup = NakamaServerStartup.new()